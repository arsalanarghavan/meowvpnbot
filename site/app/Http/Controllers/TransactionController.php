<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class TransactionController extends Controller
{
    private $dbPath;

    public function __construct()
    {
        $this->dbPath = base_path('../vpn_bot.db');
    }

    /**
     * نمایش لیست تراکنش‌ها
     */
    public function index(Request $request)
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
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
        $stats = [
            'total' => $pdo->query("SELECT COUNT(*) FROM transactions")->fetchColumn(),
            'completed' => $pdo->query("SELECT COUNT(*) FROM transactions WHERE status = 'موفق'")->fetchColumn(),
            'pending' => $pdo->query("SELECT COUNT(*) FROM transactions WHERE status = 'در انتظار'")->fetchColumn(),
            'failed' => $pdo->query("SELECT COUNT(*) FROM transactions WHERE status = 'ناموفق'")->fetchColumn(),
            'total_amount' => $pdo->query("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE status = 'موفق'")->fetchColumn(),
            'monthly_amount' => $pdo->query("
                SELECT IFNULL(SUM(amount), 0) FROM transactions 
                WHERE status = 'موفق' 
                AND datetime(created_at) >= datetime('now', '-30 days')
            ")->fetchColumn(),
        ];
        
        return view('transactions.index', compact('transactions', 'stats'));
    }

    /**
     * نمایش جزئیات تراکنش
     */
    public function show($id)
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
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
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("UPDATE transactions SET status = 'موفق' WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
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
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("UPDATE transactions SET status = 'ناموفق' WHERE id = :id");
            $stmt->execute(['id' => $id]);
            
            return response()->json(['success' => true, 'message' => 'تراکنش رد شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }
}

