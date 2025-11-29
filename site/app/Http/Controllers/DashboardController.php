<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use App\Helpers\StatusHelper;

class DashboardController extends Controller
{
    /**
     * نمایش داشبورد اصلی
     */
    public function index()
    {
        if (!$this->botDatabaseExists()) {
            return view('dashboard.index')->with('error', 'دیتابیس ربات یافت نشد!');
        }

        // آمارگیری
        $stats = $this->getDashboardStats();
        
        return view('dashboard.index', compact('stats'));
    }

    /**
     * دریافت آمار داشبورد به صورت JSON (API)
     */
    public function stats()
    {
        if (!$this->botDatabaseExists()) {
            return response()->json(['success' => false, 'message' => 'دیتابیس ربات یافت نشد!'], 404);
        }

        try {
            $stats = $this->getDashboardStats();
            return response()->json(['success' => true, 'data' => $stats]);
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()], 500);
        }
    }

    /**
     * دریافت آمار داشبورد
     */
    private function getDashboardStats()
    {
        $pdo = $this->getBotConnection();
        
        // آمار کاربران
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users");
        $stmt->execute();
        $totalUsers = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE is_active = 1");
        $stmt->execute();
        $activeUsers = $stmt->fetchColumn();
        $blockedUsers = $totalUsers - $activeUsers;
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM users WHERE role = :role");
        $stmt->execute(['role' => 'marketer']);
        $marketers = $stmt->fetchColumn();
        
        // آمار سرویس‌ها
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM services");
        $stmt->execute();
        $totalServices = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM services WHERE is_active = 1");
        $stmt->execute();
        $activeServices = $stmt->fetchColumn();
        $expiredServices = $totalServices - $activeServices;
        
        // آمار مالی
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(amount), 0) FROM transactions WHERE status = :status");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED]);
        $totalRevenue = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM transactions WHERE status = :status");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_PENDING]);
        $pendingTransactions = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("
            SELECT IFNULL(SUM(amount), 0) FROM transactions 
            WHERE status = :status 
            AND datetime(created_at) >= datetime('now', '-30 days')
        ");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED]);
        $monthlyRevenue = $stmt->fetchColumn();
        
        // تراکنش‌های امروز
        $stmt = $pdo->prepare("
            SELECT COUNT(*) FROM transactions 
            WHERE date(created_at) = date('now')
        ");
        $stmt->execute();
        $todayTransactions = $stmt->fetchColumn();
        
        // آمار پلن‌ها
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM plans");
        $stmt->execute();
        $totalPlans = $stmt->fetchColumn();
        
        // آمار پنل‌ها
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM panels");
        $stmt->execute();
        $totalPanels = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM panels WHERE is_active = 1");
        $stmt->execute();
        $activePanels = $stmt->fetchColumn();
        
        // آمار کارت‌های هدیه
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM gift_cards");
        $stmt->execute();
        $totalGiftCards = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT COUNT(*) FROM gift_cards WHERE is_used = 1");
        $stmt->execute();
        $usedGiftCards = $stmt->fetchColumn();
        $unusedGiftCards = $totalGiftCards - $usedGiftCards;
        
        // آمار کمیسیون‌ها
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions");
        $stmt->execute();
        $totalCommissions = $stmt->fetchColumn();
        
        $stmt = $pdo->prepare("SELECT IFNULL(SUM(commission_amount), 0) FROM commissions WHERE is_paid_out = 0");
        $stmt->execute();
        $unpaidCommissions = $stmt->fetchColumn();
        
        // آخرین کاربران
        $stmt = $pdo->prepare("
            SELECT user_id, role, wallet_balance, created_at, is_active 
            FROM users 
            ORDER BY created_at DESC 
            LIMIT 10
        ");
        $stmt->execute();
        $latestUsers = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آخرین تراکنش‌ها
        $stmt = $pdo->prepare("
            SELECT t.*, u.user_id 
            FROM transactions t
            LEFT JOIN users u ON t.user_id = u.user_id
            ORDER BY t.created_at DESC 
            LIMIT 10
        ");
        $stmt->execute();
        $latestTransactions = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
        // آمار سرویس‌های در حال انقضا (7 روز آینده)
        $stmt = $pdo->prepare("
            SELECT COUNT(*) FROM services 
            WHERE is_active = 1 
            AND datetime(expire_date) <= datetime('now', '+7 days')
            AND datetime(expire_date) >= datetime('now')
        ");
        $stmt->execute();
        $expiringServices = $stmt->fetchColumn();
        
        // نمودار درآمد 30 روز اخیر
        $stmt = $pdo->prepare("
            SELECT date(created_at) as date, SUM(amount) as total
            FROM transactions 
            WHERE status = :status 
            AND datetime(created_at) >= datetime('now', '-30 days')
            GROUP BY date(created_at)
            ORDER BY date
        ");
        $stmt->execute(['status' => StatusHelper::TRANSACTION_COMPLETED]);
        $revenueChart = $stmt->fetchAll(\PDO::FETCH_ASSOC);
        
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
            'transactions' => [
                'today' => $todayTransactions,
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
            'recentUsers' => $latestUsers,
            'latestTransactions' => $latestTransactions,
            'recentTransactions' => $latestTransactions,
            'revenueChart' => $revenueChart,
        ];
    }
}

