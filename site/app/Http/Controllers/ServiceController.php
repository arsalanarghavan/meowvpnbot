<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class ServiceController extends Controller
{
    /**
     * نمایش لیست سرویس‌ها
     */
    public function index(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        // فیلترها
        $search = $request->get('search');
        $status = $request->get('status');
        $planId = $request->get('plan_id');
        
        $query = "
            SELECT s.*, u.user_id, p.name as plan_name, p.category, p.price
            FROM services s
            LEFT JOIN users u ON s.user_id = u.user_id
            LEFT JOIN plans p ON s.plan_id = p.id
            WHERE 1=1
        ";
        $params = [];
        
        if ($search) {
            $query .= " AND (s.username_in_panel LIKE :search OR u.user_id LIKE :search2)";
            $params['search'] = "%{$search}%";
            $params['search2'] = "%{$search}%";
        }
        
        if ($status && $status != 'all') {
            $active = $status == 'active' ? 1 : 0;
            $query .= " AND s.is_active = :status";
            $params['status'] = $active;
        }
        
        if ($planId && $planId != 'all') {
            $query .= " AND s.plan_id = :plan_id";
            $params['plan_id'] = $planId;
        }
        
        $query .= " ORDER BY s.start_date DESC LIMIT 100";
        
        $stmt = $pdo->prepare($query);
        $stmt->execute($params);
        $services = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // لیست پلن‌ها برای فیلتر
        $stmt = $pdo->prepare("SELECT id, name, category FROM plans ORDER BY name");
        $stmt->execute();
        $plans = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM services");
        $stmt->execute();
        $stats['total'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM services WHERE is_active = 1");
        $stmt->execute();
        $stats['active'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM services WHERE is_active = 0");
        $stmt->execute();
        $stats['expired'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("
            SELECT COUNT(*) FROM services 
            WHERE is_active = 1 
            AND datetime(expire_date) <= datetime('now', '+7 days')
            AND datetime(expire_date) >= datetime('now')
        ");
        $stmt->execute();
        $stats['expiring_soon'] = $stmt->fetchColumn();
        
        return view('services.index', compact('services', 'plans', 'stats'));
    }

    /**
     * نمایش جزئیات سرویس
     */
    public function show($id)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        // اطلاعات سرویس
        $stmt = $pdo->prepare("
            SELECT s.*, u.user_id, u.role, p.name as plan_name, p.category, p.price, p.duration_days, p.traffic_gb, p.device_limit
            FROM services s
            LEFT JOIN users u ON s.user_id = u.user_id
            LEFT JOIN plans p ON s.plan_id = p.id
            WHERE s.id = :id
        ");
        $stmt->execute(['id' => $id]);
        $service = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$service) {
            return redirect()->back()->with('error', 'سرویس یافت نشد!');
        }
        
        // محاسبه روزهای باقیمانده
        $expireDate = new \DateTime($service['expire_date']);
        $now = new \DateTime();
        $remainingDays = $now->diff($expireDate)->days;
        if ($expireDate < $now) {
            $remainingDays = -$remainingDays;
        }
        
        $service['remaining_days'] = $remainingDays;
        
        return view('services.show', compact('service'));
    }

    /**
     * غیرفعال/فعال کردن سرویس
     */
    public function toggleStatus($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                UPDATE services 
                SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END 
                WHERE id = :id
            ");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'وضعیت سرویس تغییر کرد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * حذف سرویس
     */
    public function destroy($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("DELETE FROM services WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'سرویس با موفقیت حذف شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * دریافت لیست سرویس‌ها به صورت JSON (API)
     */
    public function apiIndex(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $query = "
                SELECT s.*, u.user_id, p.name as plan_name 
                FROM services s
                LEFT JOIN users u ON s.user_id = u.user_id
                LEFT JOIN plans p ON s.plan_id = p.id
                WHERE 1=1
            ";
            $params = [];
            
            if ($request->has('status')) {
                $query .= " AND s.is_active = :status";
                $params['status'] = $request->get('status') === 'active' ? 1 : 0;
            }
            
            $query .= " ORDER BY s.created_at DESC LIMIT 100";
            
            $stmt = $pdo->prepare($query);
            $stmt->execute($params);
            $services = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            return response()->json(['success' => true, 'data' => $services]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت جزئیات سرویس به صورت JSON (API)
     */
    public function apiShow($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                SELECT s.*, u.user_id, u.role, p.name as plan_name, p.category
                FROM services s
                LEFT JOIN users u ON s.user_id = u.user_id
                LEFT JOIN plans p ON s.plan_id = p.id
                WHERE s.id = :id
            ");
            $stmt->execute(['id' => $id]);
            $service = $stmt->fetch(\PDO::FETCH_ASSOC);
            
            if (!$service) {
                return response()->json(['success' => false, 'message' => 'سرویس یافت نشد!'], 404);
            }
            
            return response()->json(['success' => true, 'data' => $service]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}

