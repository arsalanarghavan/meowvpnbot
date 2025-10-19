<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class DashboardController extends Controller
{
    /**
     * نمایش داشبورد اصلی
     */
    public function index()
    {
        // اتصال به دیتابیس SQLite ربات
        $botDbPath = base_path('../vpn_bot.db');
        
        if (!file_exists($botDbPath)) {
            return view('dashboard.index')->with('error', 'دیتابیس ربات یافت نشد!');
        }

        // آمارگیری
        $stats = $this->getDashboardStats($botDbPath);
        
        return view('dashboard.index', compact('stats'));
    }

    /**
     * دریافت آمار داشبورد
     */
    private function getDashboardStats($dbPath)
    {
        $pdo = new \PDO("sqlite:$dbPath");
        
        // آمار کاربران
        $totalUsers = $pdo->query("SELECT COUNT(*) FROM users")->fetchColumn();
        $activeUsers = $pdo->query("SELECT COUNT(*) FROM users WHERE is_active = 1")->fetchColumn();
        $blockedUsers = $totalUsers - $activeUsers;
        $marketers = $pdo->query("SELECT COUNT(*) FROM users WHERE role = 'marketer'")->fetchColumn();
        
        // آمار سرویس‌ها
        $totalServices = $pdo->query("SELECT COUNT(*) FROM services")->fetchColumn();
        $activeServices = $pdo->query("SELECT COUNT(*) FROM services WHERE is_active = 1")->fetchColumn();
        $expiredServices = $totalServices - $activeServices;
        
        // آمار مالی
        $totalRevenue = $pdo->query("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE status = 'موفق'")->fetchColumn();
        $pendingTransactions = $pdo->query("SELECT COUNT(*) FROM transactions WHERE status = 'در انتظار'")->fetchColumn();
        $monthlyRevenue = $pdo->query("
            SELECT IFNULL(SUM(amount), 0) FROM transactions 
            WHERE status = 'موفق' 
            AND datetime(created_at) >= datetime('now', '-30 days')
        ")->fetchColumn();
        
        // آمار پلن‌ها
        $totalPlans = $pdo->query("SELECT COUNT(*) FROM plans")->fetchColumn();
        
        // آمار پنل‌ها
        $totalPanels = $pdo->query("SELECT COUNT(*) FROM panels")->fetchColumn();
        $activePanels = $pdo->query("SELECT COUNT(*) FROM panels WHERE is_active = 1")->fetchColumn();
        
        // آمار کارت‌های هدیه
        $totalGiftCards = $pdo->query("SELECT COUNT(*) FROM gift_cards")->fetchColumn();
        $usedGiftCards = $pdo->query("SELECT COUNT(*) FROM gift_cards WHERE is_used = 1")->fetchColumn();
        $unusedGiftCards = $totalGiftCards - $usedGiftCards;
        
        // آمار کمیسیون‌ها
        $totalCommissions = $pdo->query("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions")->fetchColumn();
        $unpaidCommissions = $pdo->query("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE is_paid_out = 0")->fetchColumn();
        
        // آخرین کاربران
        $latestUsers = $pdo->query("
            SELECT user_id, role, wallet_balance, created_at, is_active 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        ")->fetchAll(\PDO::FETCH_ASSOC);
        
        // آخرین تراکنش‌ها
        $latestTransactions = $pdo->query("
            SELECT t.*, u.user_id 
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.user_id
            ORDER BY t.created_at DESC 
            LIMIT 10
        ")->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار سرویس‌های در حال انقضا (7 روز آینده)
        $expiringServices = $pdo->query("
            SELECT COUNT(*) FROM services 
            WHERE is_active = 1 
            AND datetime(expire_date) <= datetime('now', '+7 days')
            AND datetime(expire_date) >= datetime('now')
        ")->fetchColumn();
        
        // نمودار درآمد 30 روز اخیر
        $revenueChart = $pdo->query("
            SELECT date(created_at) as date, SUM(amount) as total
            FROM transactions 
            WHERE status = 'موفق' 
            AND datetime(created_at) >= datetime('now', '-30 days')
            GROUP BY date(created_at)
            ORDER BY date
        ")->fetchAll(\PDO::FETCH_ASSOC);
        
        return [
            'users' => [
                'total' => $totalUsers,
                'active' => $activeUsers,
                'blocked' => $blockedUsers,
                'marketers' => $marketers,
            ],
            'services' => [
                'total' => $totalServices,
                'active' => $activeServices,
                'expired' => $expiredServices,
                'expiring' => $expiringServices,
            ],
            'revenue' => [
                'total' => $totalRevenue,
                'monthly' => $monthlyRevenue,
                'pending' => $pendingTransactions,
            ],
            'plans' => [
                'total' => $totalPlans,
            ],
            'panels' => [
                'total' => $totalPanels,
                'active' => $activePanels,
            ],
            'giftCards' => [
                'total' => $totalGiftCards,
                'used' => $usedGiftCards,
                'unused' => $unusedGiftCards,
            ],
            'commissions' => [
                'total' => $totalCommissions,
                'unpaid' => $unpaidCommissions,
            ],
            'latestUsers' => $latestUsers,
            'latestTransactions' => $latestTransactions,
            'revenueChart' => $revenueChart,
        ];
    }
}

