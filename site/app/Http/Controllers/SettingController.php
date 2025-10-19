<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class SettingController extends Controller
{
    private $dbPath;

    public function __construct()
    {
        $this->dbPath = base_path('../vpn_bot.db');
    }

    /**
     * نمایش صفحه تنظیمات
     */
    public function index()
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        $pdo = new \PDO("sqlite:{$this->dbPath}");
        
        // خواندن تنظیمات
        $settings = $pdo->query("SELECT * FROM settings")->fetchAll(\PDO::FETCH_ASSOC);
        
        // تبدیل به آرایه key => value
        $settingsArray = [];
        foreach ($settings as $setting) {
            $settingsArray[$setting['key']] = $setting['value'];
        }
        
        return view('settings.index', compact('settingsArray'));
    }

    /**
     * ذخیره تنظیمات
     */
    public function update(Request $request)
    {
        if (!file_exists($this->dbPath)) {
            return redirect()->back()->with('error', 'دیتابیس ربات یافت نشد!');
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            // لیست کلیدهای تنظیمات قابل ویرایش
            $allowedKeys = [
                'card_number',
                'card_holder_name',
                'zarinpal_merchant_id',
                'support_username',
                'channel_id',
                'test_account_duration_days',
                'test_account_traffic_gb',
                'commission_percentage',
                'minimum_payout_amount',
                'bot_welcome_message',
                'purchase_success_message',
                'service_expiring_message',
            ];
            
            foreach ($allowedKeys as $key) {
                if ($request->has($key)) {
                    $value = $request->input($key);
                    
                    // بررسی وجود کلید
                    $stmt = $pdo->prepare("SELECT COUNT(*) FROM settings WHERE key = :key");
                    $stmt->execute(['key' => $key]);
                    $exists = $stmt->fetchColumn() > 0;
                    
                    if ($exists) {
                        // به‌روزرسانی
                        $stmt = $pdo->prepare("UPDATE settings SET value = :value WHERE key = :key");
                        $stmt->execute(['value' => $value, 'key' => $key]);
                    } else {
                        // درج
                        $stmt = $pdo->prepare("INSERT INTO settings (key, value) VALUES (:key, :value)");
                        $stmt->execute(['key' => $key, 'value' => $value]);
                    }
                }
            }
            
            return redirect()->back()->with('success', 'تنظیمات با موفقیت ذخیره شد!');
            
        } catch (\Exception $e) {
            return redirect()->back()->with('error', $e->getMessage());
        }
    }

    /**
     * دریافت یک تنظیم خاص
     */
    public function getSetting($key)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            
            $stmt = $pdo->prepare("SELECT value FROM settings WHERE key = :key");
            $stmt->execute(['key' => $key]);
            $value = $stmt->fetchColumn();
            
            return response()->json(['success' => true, 'value' => $value]);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }

    /**
     * تنظیم یک مقدار
     */
    public function setSetting(Request $request, $key)
    {
        if (!file_exists($this->dbPath)) {
            return response()->json(['success' => false, 'message' => 'دیتابیس یافت نشد!']);
        }

        try {
            $pdo = new \PDO("sqlite:{$this->dbPath}");
            $value = $request->input('value');
            
            // بررسی وجود کلید
            $stmt = $pdo->prepare("SELECT COUNT(*) FROM settings WHERE key = :key");
            $stmt->execute(['key' => $key]);
            $exists = $stmt->fetchColumn() > 0;
            
            if ($exists) {
                $stmt = $pdo->prepare("UPDATE settings SET value = :value WHERE key = :key");
            } else {
                $stmt = $pdo->prepare("INSERT INTO settings (key, value) VALUES (:key, :value)");
            }
            
            $stmt->execute(['key' => $key, 'value' => $value]);
            
            return response()->json(['success' => true, 'message' => 'تنظیم با موفقیت ذخیره شد!']);
            
        } catch (\Exception $e) {
            return response()->json(['success' => false, 'message' => $e->getMessage()]);
        }
    }
}
