<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class MarketerController extends Controller
{
    private $dbPath;

    public function __construct()
    {
        $this->dbPath = base_path('../vpn_bot.db');
    }

    /**
     * نمایش لیست بازاریاب‌ها
     */
    public function index()
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        // لیست بازاریاب‌ها
        $marketers = $pdo->query("
            SELECT * FROM users 
            WHERE role = 'marketer' 
            ORDER BY created_at DESC
        ")->fetchAll(\PDO::FETCH_ASSOC);
        
        // محاسبه آمار هر بازاریاب
        foreach ($marketers as &$marketer) {
            $userId = $marketer['user_id'];
            
            // تعداد معرفی‌ها
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE referrer_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            $marketer['referrals_count'] = $stmt->fetchColumn();
            
            // تعداد کمیسیون‌ها
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM commissions WHERE marketer_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            $marketer['commissions_count'] = $stmt->fetchColumn();
            
            // مجموع کمیسیون‌ها
            $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE marketer_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            $marketer['total_commission'] = $stmt->fetchColumn();
            
            // کمیسیون‌های پرداخت نشده
            $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE marketer_id = :user_id AND is_paid_out = 0");
            $stmt->execute(['user_id' => $userId]);
            $marketer['unpaid_commission'] = $stmt->fetchColumn();
        }
        
        // آمار کلی
        $stats = [
            'total' => count($marketers),
            'total_commissions' => $pdo->query("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions")->fetchColumn(),
            'unpaid_commissions' => $pdo->query("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE is_paid_out = 0")->fetchColumn(),
            'total_referrals' => $pdo->query("SELECT COUNT(*) FROM users WHERE referrer_id IS NOT NULL")->fetchColumn(),
        ];
        
        return view('marketers.index', compact('marketers', 'stats'));
    }

    /**
     * نمایش جزئیات بازاریاب
     */
    public function show($userId)
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        // اطلاعات بازاریاب
        $stmt = $pdo->prepare("SELECT * FROM users WHERE user_id = :user_id AND role = 'marketer'");
        $stmt->execute(['user_id' => $userId]);
        $marketer = $stmt->fetch(\PDO::FETCH_ASSOC);
        
        if (!$marketer) {
            return redirect()->back()->with('error', 'بازاریاب یافت نشد!');
        }
        
        // لیست معرفی شده‌ها
        $stmt = $pdo->prepare("
            SELECT * FROM users 
            WHERE referrer_id = :user_id 
            ORDER BY created_at DESC
        ");
        $stmt->execute(['user_id' => $userId]);
        $referrals = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // لیست کمیسیون‌ها
        $stmt = $pdo->prepare("
            SELECT c.*, t.amount as transaction_amount, t.type, u.user_id as referred_user
            FROM commissions c
            LEFT JOIN transactions t ON c.transaction_id = t.id
            LEFT JOIN users u ON c.referred_user_id = u.user_id
            WHERE c.marketer_id = :user_id
            ORDER BY c.created_at DESC
        ");
        $stmt->execute(['user_id' => $userId]);
        $commissions = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار
        $stats = [
            'total_referrals' => count($referrals),
            'total_commissions' => array_sum(array_column($commissions, 'commission_amount')),
            'unpaid_commissions' => array_sum(array_map(function($c) {
                return $c['is_paid_out'] == 0 ? $c['commission_amount'] : 0;
            }, $commissions)),
            'paid_commissions' => array_sum(array_map(function($c) {
                return $c['is_paid_out'] == 1 ? $c['commission_amount'] : 0;
            }, $commissions)),
        ];
        
        return view('marketers.show', compact('marketer', 'referrals', 'commissions', 'stats'));
    }

    /**
     * تسویه حساب بازاریاب
     */
    public function payout($userId)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            $pdo->beginTransaction();
            
            // محاسبه کمیسیون‌های پرداخت نشده
            $stmt = $pdo->prepare("
                SELECT IFNULL(SUM(commission_amount), 0) 
                FROM commissions 
                WHERE marketer_id = :user_id AND is_paid_out = 0
            ");
            $stmt->execute(['user_id' => $userId]);
            $unpaidAmount = $stmt->fetchColumn();
            
            if ($unpaidAmount <= 0) {
                $pdo->rollBack();
                return response()->json(['success' => false, 'message' => 'کمیسیون پرداخت نشده‌ای وجود ندارد!']);
            }
            
            // علامت‌گذاری کمیسیون‌ها به عنوان پرداخت شده
            $stmt = $pdo->prepare("
                UPDATE commissions 
                SET is_paid_out = 1 
                WHERE marketer_id = :user_id AND is_paid_out = 0
            ");
            $stmt->execute(['user_id' => $userId]);
            
            // کاهش موجودی کمیسیون
            $stmt = $pdo->prepare("
                UPDATE users 
                SET commission_balance = 0 
                WHERE user_id = :user_id
            ");
            $stmt->execute(['user_id' => $userId]);
            
            $pdo->commit();
            
            return response()->json([
                'success' => true, 
                'message' => 'تسویه حساب با موفقیت انجام شد!',
                'amount' => $unpaidAmount
            ]);
            
        } catch (\Exception $e) {
            $pdo->rollBack();
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }
}

