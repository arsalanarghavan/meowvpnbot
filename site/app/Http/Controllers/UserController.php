<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class UserController extends Controller
{
    /**
     * نمایش لیست کاربران
     */
    public function index(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        // فیلترها
        $search = $request->get('search');
        $role = $request->get('role');
        $status = $request->get('status');
        
        $query = "SELECT * FROM users WHERE 1=1";
        $params = [];
        
        if ($search) {
            $query .= " AND user_id LIKE :search";
            $params['search'] = "%{$search}%";
        }
        
        if ($role && $role != 'all') {
            $query .= " AND role = :role";
            $params['role'] = $role;
        }
        
        if ($status && $status != 'all') {
            $active = $status == 'active' ? 1 : 0;
            $query .= " AND is_active = :status";
            $params['status'] = $active;
        }
        
        $query .= " ORDER BY created_at DESC LIMIT 100";
        
        $stmt = $pdo->prepare($query);
        $stmt->execute($params);
        $users = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار کلی
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users");
        $stmt->execute();
        $stats['total'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE is_active = 1");
        $stmt->execute();
        $stats['active'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE role = :role");
        $stmt->execute(['role' => 'customer']);
        $stats['customers'] = $stmt->fetchColumn();
        
        $stmt->execute(['role' => 'marketer']);
        $stats['marketers'] = $stmt->fetchColumn();
        
        $stmt->execute(['role' => 'admin']);
        $stats['admins'] = $stmt->fetchColumn();
        
        return view('users.index', compact('users', 'stats'));
    }

    /**
     * نمایش جزئیات کاربر
     */
    public function show($userId)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        // اطلاعات کاربر
        $stmt = $pdo->prepare("SELECT * FROM users WHERE user_id = :user_id");
        $stmt->execute(['user_id' => $userId]);
        $user = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$user) {
            return redirect()->back()->with('error', 'کاربر یافت نشد!');
        }
        
        // سرویس‌های کاربر
        $stmt = $pdo->prepare("
            SELECT s.*, p.name as plan_name, p.category 
            FROM services s
            LEFT JOIN plans p ON s.plan_id = p.id
            WHERE s.user_id = :user_id
            ORDER BY s.created_at DESC
        ");
        $stmt->execute(['user_id' => $userId]);
        $services = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // تراکنش‌های کاربر
        $stmt = $pdo->prepare("
            SELECT * FROM transactions 
            WHERE user_id = :user_id 
            ORDER BY created_at DESC 
            LIMIT 50
        ");
        $stmt->execute(['user_id' => $userId]);
        $transactions = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // اگر بازاریاب است
        $referrals = [];
        $commissions = [];
        if ($user['role'] == 'marketer') {
            // افراد معرفی شده
            $stmt = $pdo->prepare("
                SELECT * FROM users 
                WHERE referrer_id = :user_id 
                ORDER BY created_at DESC
            ");
            $stmt->execute(['user_id' => $userId]);
            $referrals = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            // کمیسیون‌ها
            $stmt = $pdo->prepare("
                SELECT c.*, t.amount as transaction_amount, u.user_id as referred_user
                FROM commissions c
                LEFT JOIN transactions t ON c.transaction_id = t.id
                LEFT JOIN users u ON c.referred_user_id = u.user_id
                WHERE c.marketer_id = :user_id
                ORDER BY c.created_at DESC
            ");
            $stmt->execute(['user_id' => $userId]);
            $commissions = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        }
        
        return view('users.show', compact('user', 'services', 'transactions', 'referrals', 'commissions'));
    }

    /**
     * ویرایش کاربر
     */
    public function update(Request $request, $userId)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        $pdo = $this->getBotConnection();
        
        $action = $request->input('action');
        
        try {
            switch ($action) {
                case 'toggle_status':
                    $stmt = $pdo->prepare("
                        UPDATE users 
                        SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
                        WHERE user_id = :user_id
                    ");
                    $stmt->execute(['user_id' => $userId]);
                    break;
                    
                case 'change_role':
                    $role = $request->input('role');
                    $stmt = $pdo->prepare("UPDATE users SET role = :role WHERE user_id = :user_id");
                    $stmt->execute(['role' => $role, 'user_id' => $userId]);
                    break;
                    
                case 'add_balance':
                    $amount = $request->input('amount');
                    $stmt = $pdo->prepare("
                        UPDATE users 
                        SET wallet_balance = wallet_balance + :amount 
                        WHERE user_id = :user_id
                    ");
                    $stmt->execute(['amount' => $amount, 'user_id' => $userId]);
                    break;
                    
                case 'set_balance':
                    $balance = $request->input('balance');
                    $stmt = $pdo->prepare("UPDATE users SET wallet_balance = :balance WHERE user_id = :user_id");
                    $stmt->execute(['balance' => $balance, 'user_id' => $userId]);
                    break;
            }
            
            return response()->json(['success' => true, 'message' => 'عملیات با موفقیت انجام شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * حذف کاربر
     */
    public function destroy($userId)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            // حذف کاربر (در صورت نیاز می‌توان سرویس‌ها را هم حذف کرد)
            $stmt = $pdo->prepare("DELETE FROM users WHERE user_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            
            return response()->json(['success' => true, 'message' => 'کاربر با موفقیت حذف شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * دریافت لیست کاربران به صورت JSON (API)
     */
    public function apiIndex(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $query = "SELECT * FROM users WHERE 1=1";
            $params = [];
            
            if ($request->has('role')) {
                $query .= " AND role = :role";
                $params['role'] = $request->get('role');
            }
            
            if ($request->has('search')) {
                $query .= " AND user_id LIKE :search";
                $params['search'] = "%" . $request->get('search') . "%";
            }
            
            $query .= " ORDER BY created_at DESC LIMIT 100";
            
            $stmt = $pdo->prepare($query);
            $stmt->execute($params);
            $users = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            return response()->json(['success' => true, 'data' => $users]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت جزئیات کاربر به صورت JSON (API)
     */
    public function apiShow($userId)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("SELECT * FROM users WHERE user_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            $user = $stmt->fetch(\PDO::FETCH_ASSOC);
            
            if (!$user) {
                return response()->json(['success' => false, 'message' => 'کاربر یافت نشد!'], 404);
            }
            
            return response()->json(['success' => true, 'data' => $user]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}

