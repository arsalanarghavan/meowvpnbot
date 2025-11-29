<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Helpers\StatusHelper;

class TransactionController extends Controller
{
    /**
     * نمایش لیست تراکنش‌ها
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
        $type = $request->get('type');
        
        $query = "
            SELECT t.*, u.user_id, p.name as plan_name
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN plans p ON t.plan_id = p.id
            WHERE 1=1
        ";
        $params = [];
        
        if ($search) {
            $query .= " AND (t.tracking_code LIKE :search OR u.user_id LIKE :search2)";
            $params['search'] = "%{$search}%";
            $params['search2'] = "%{$search}%";
        }
        
        if ($status && $status != 'all') {
            $query .= " AND t.status = :status";
            $params['status'] = $status;
        }
        
        if ($type && $type != 'all') {
            $query .= " AND t.type = :type";
            $params['type'] = $type;
        }
        
        $query .= " ORDER BY t.created_at DESC LIMIT 200";
        
        $stmt = $pdo->prepare($query);
        $stmt->execute($params);
        $transactions = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM transactions");
        $stmt->execute();
        $stats['total'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM transactions WHERE status = :status");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED]);
        $stats['completed'] = $stmt->fetchColumn();
        
        $stmt->execute(['status' => StatusHelper::TRANSACTION_PENDING]);
        $stats['pending'] = $stmt->fetchColumn();
        
        $stmt->execute(['status' => StatusHelper::TRANSACTION_FAILED]);
        $stats['failed'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE status = :status");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED]);
        $stats['total_amount'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("
            SELECT IFNULL(SUM(amount), 0) FROM transactions 
            WHERE status = :status 
            AND datetime(created_at) >= datetime('now', '-30 days')
        ");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED]);
        $stats['monthly_amount'] = $stmt->fetchColumn();
        
        return view('transactions.index', compact('transactions', 'stats'));
    }

    /**
     * نمایش جزئیات تراکنش
     */
    public function show($id)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        $stmt = $pdo->prepare("
            SELECT t.*, u.user_id, u.role, p.name as plan_name, p.category
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.user_id
            LEFT JOIN plans p ON t.plan_id = p.id
            WHERE t.id = :id
        ");
        $stmt->execute(['id' => $id]);
        $transaction = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$transaction) {
            return redirect()->back()->with('error', 'تراکنش یافت نشد!');
        }
        
        return view('transactions.show', compact('transaction'));
    }

    /**
     * تایید تراکنش
     */
    public function approve($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("UPDATE transactions SET status = :status WHERE id = :id");
            $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED, 'id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'تراکنش تایید شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * رد تراکنش
     */
    public function reject($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("UPDATE transactions SET status = :status WHERE id = :id");
            $stmt->execute(['status' => StatusHelper::TRANSACTION_FAILED, 'id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'تراکنش رد شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * دریافت لیست تراکنش‌ها به صورت JSON (API)
     */
    public function apiIndex(Request $request)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $query = "
                SELECT t.*, u.user_id, p.name as plan_name
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.user_id
                LEFT JOIN plans p ON t.plan_id = p.id
                WHERE 1=1
            ";
            $params = [];
            
            if ($request->has('status')) {
                $query .= " AND t.status = :status";
                $params['status'] = $request->get('status');
            }
            
            if ($request->has('type')) {
                $query .= " AND t.type = :type";
                $params['type'] = $request->get('type');
            }
            
            $query .= " ORDER BY t.created_at DESC LIMIT 200";
            
            $stmt = $pdo->prepare($query);
            $stmt->execute($params);
            $transactions = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            return response()->json(['success' => true, 'data' => $transactions]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت جزئیات تراکنش به صورت JSON (API)
     */
    public function apiShow($id)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                SELECT t.*, u.user_id, u.role, p.name as plan_name, p.category
                FROM transactions t
                LEFT JOIN users u ON t.user_id = u.user_id
                LEFT JOIN plans p ON t.plan_id = p.id
                WHERE t.id = :id
            ");
            $stmt->execute(['id' => $id]);
            $transaction = $stmt->fetch(\PDO::FETCH_ASSOC);
            
            if (!$transaction) {
                return response()->json(['success' => false, 'message' => 'تراکنش یافت نشد!'], 404);
            }
            
            return response()->json(['success' => true, 'data' => $transaction]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}

