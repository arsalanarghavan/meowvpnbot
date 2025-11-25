<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class AuthController extends Controller
{
    /**
     * نمایش صفحه لاگین
     */
    public function showLogin()
    {
        // اگر لاگین کرده، به dashboard برو
        if (session()->has('user_authenticated')) {
            return redirect()->route('dashboard');
        }

        // اگر admin نساخته نشده، به welcome برو
        if (empty(env('ADMIN_USERNAME'))) {
            return redirect()->route('setup.welcome');
        }

        return view('auth.login');
    }

    /**
     * پردازش لاگین
     */
    public function login(Request $request)
    {
        $request->validate([
            'username' => 'required',
            'password' => 'required',
        ]);

        $username = $request->input('username');
        $password = $request->input('password');

        // دریافت اطلاعات از .env
        $adminUsername = env('ADMIN_USERNAME');
        $adminPassword = env('ADMIN_PASSWORD');

        // بررسی وجود اطلاعات ادمین
        if (empty($adminUsername) || empty($adminPassword)) {
            return back()->withErrors([
                'username' => 'سیستم هنوز تنظیم نشده است. لطفاً ابتدا Setup Wizard را تکمیل کنید.',
            ])->withInput($request->only('username'));
        }

        // بررسی ادمین
        if ($username === $adminUsername && $password === $adminPassword) {
            session([
                'user_authenticated' => true,
                'user_role' => 'admin',
                'username' => $username,
            ]);

            // اگر Setup Wizard هنوز فعال است، redirect به setup
            if (env('SETUP_WIZARD_ENABLED', false) && !env('BOT_INSTALLED', false)) {
                return redirect()->route('setup')->with('info', 'لطفاً Setup Wizard را تکمیل کنید.');
            }

            return redirect()->route('dashboard')->with('success', 'خوش آمدید!');
        }

        // چک کردن بازاریاب‌های دیتابیس (اختیاری - برای آینده)
        $dbPath = base_path('../vpn_bot.db');
        if (file_exists($dbPath)) {
            try {
                $pdo = new \PDO("sqlite:$dbPath");

                // چک کردن در جدول settings برای بازاریاب‌های اضافی
                $stmt = $pdo->prepare("SELECT value FROM settings WHERE key = :key");
                $stmt->execute(['key' => 'marketer_' . $username]);
                $storedPassword = $stmt->fetchColumn();

                if ($storedPassword && password_verify($password, $storedPassword)) {
                    session([
                        'user_authenticated' => true,
                        'user_role' => 'marketer',
                        'username' => $username,
                    ]);

                    return redirect()->route('marketers.index')->with('success', 'خوش آمدید!');
                }
            } catch (\Exception $e) {
                // در صورت خطا، ادامه بده
            }
        }

        // اگر اطلاعات نادرست بود
        return back()->withErrors([
            'username' => 'نام کاربری یا رمز عبور اشتباه است.',
        ])->withInput($request->only('username'));
    }

    /**
     * خروج از حساب
     */
    public function logout()
    {
        session()->flush();
        return redirect()->route('login')->with('success', 'با موفقیت خارج شدید.');
    }
}

