<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class MarketerController extends Controller
{
    /**
     * نمایش لیست بازاریاب‌ها
     */
    public function index()
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
        // لیست بازاریاب‌ها
        $stmt = $pdo->prepare("
            SELECT * FROM users 
            WHERE role = :role 
            ORDER BY created_at DESC
        ");
        $stmt->execute(['role' => 'marketer']);
        $marketers = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
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
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions");
        $stmt->execute();
        $stats['total_commissions'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE is_paid_out = 0");
        $stmt->execute();
        $stats['unpaid_commissions'] = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE referrer_id IS NOT NULL");
        $stmt->execute();
        $stats['total_referrals'] = $stmt->fetchColumn();
        
        $stats['total'] = count($marketers);
        
        return view('marketers.index', compact('marketers', 'stats'));
    }

    /**
     * نمایش جزئیات بازاریاب
     */
    public function show($userId)
    {
        if (!$this->botDatabaseExists()) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = $this->getBotConnection();
        
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
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = $this->getBotConnection();
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

    /**
     * دریافت لیست بازاریاب‌ها به صورت JSON (API)
     */
    public function apiIndex()
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("
                SELECT * FROM users 
                WHERE role = :role 
                ORDER BY created_at DESC
            ");
            $stmt->execute(['role' => 'marketer']);
            $marketers = $stmt->fetchAll(\PDO::FETCH_ASSOC);
            
            // محاسبه آمار هر بازاریاب
            foreach ($marketers as &$marketer) {
                $userId = $marketer['user_id'];
                
                $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE referrer_id = :user_id");
                $stmt->execute(['user_id' => $userId]);
                $marketer['referrals_count'] = $stmt->fetchColumn();
                
                $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE marketer_id = :user_id");
                $stmt->execute(['user_id' => $userId]);
                $marketer['total_commission'] = $stmt->fetchColumn();
            }
            
            return response()->json(['success' => true, 'data' => $marketers]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت جزئیات بازاریاب به صورت JSON (API)
     */
    public function apiShow($userId)
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $pdo = $this->getBotConnection();
            
            $stmt = $pdo->prepare("SELECT * FROM users WHERE user_id = :user_id AND role = 'marketer'");
            $stmt->execute(['user_id' => $userId]);
            $marketer = $stmt->fetch(\PDO::FETCH_ASSOC);
            
            if (!$marketer) {
                return response()->json(['success' => false, 'message' => 'بازاریاب یافت نشد!'], 404);
            }
            
            // آمار اضافی
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE referrer_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            $marketer['referrals_count'] = $stmt->fetchColumn();
            
            $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE marketer_id = :user_id");
            $stmt->execute(['user_id' => $userId]);
            $marketer['total_commission'] = $stmt->fetchColumn();
            
            return response()->json(['success' => true, 'data' => $marketer]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }
}

