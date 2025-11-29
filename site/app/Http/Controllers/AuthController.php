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

        // بررسی ادمین - فقط password hash شده را قبول می‌کنیم
        $isPasswordValid = false;
        if (password_verify($password, $adminPassword)) {
            // Password hash شده و معتبر است
            $isPasswordValid = true;
            
            // اگر password نیاز به rehash دارد، آن را به‌روزرسانی کن
            if (password_needs_rehash($adminPassword, PASSWORD_DEFAULT)) {
                $newHash = password_hash($password, PASSWORD_DEFAULT);
                // به‌روزرسانی در .env (اختیاری - می‌توانید از دیتابیس استفاده کنید)
                // این بخش را می‌توانید در صورت نیاز پیاده‌سازی کنید
            }
        }
        
        if ($username === $adminUsername && $isPasswordValid) {
            // Log successful login
            \Log::info('AUDIT: Login SUCCESS', [
                'username' => $username,
                'ip' => $request->ip(),
                'user_agent' => $request->userAgent(),
                'timestamp' => now()->toIso8601String()
            ]);
            
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
        if ($this->botDatabaseExists()) {
            try {
                $pdo = $this->getBotConnection();

                // Sanitize username for use in key (only alphanumeric and underscore)
                $sanitizedUsername = preg_replace('/[^a-zA-Z0-9_]/', '', $username);
                
                // چک کردن در جدول settings برای بازاریاب‌های اضافی
                $stmt = $pdo->prepare("SELECT value FROM settings WHERE key = :key");
                $stmt->execute(['key' => 'marketer_' . $sanitizedUsername]);
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

        // Log failed login attempt
        \Log::warning('AUDIT: Login FAILED', [
            'username' => $username,
            'ip' => $request->ip(),
            'user_agent' => $request->userAgent(),
            'timestamp' => now()->toIso8601String()
        ]);
        
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

