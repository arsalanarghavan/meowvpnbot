<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Artisan;

class SetupWizardController extends Controller
{
    private $projectRoot;

    public function __construct()
    {
        $this->projectRoot = base_path('..');
    }

    /**
     * بررسی دسترسی به Setup Wizard
     */
    private function checkWizardAccess()
    {
        // بررسی فعال بودن wizard
        if (!env('SETUP_WIZARD_ENABLED', false)) {
            return false;
        }

        // بررسی نصب شدن ربات
        if (env('BOT_INSTALLED', false)) {
            return false;
        }

        return true;
    }

    /**
     * صفحه اصلی Setup Wizard
     */
    public function index()
    {
        if (!$this->checkWizardAccess()) {
            return redirect()->route('dashboard')->with('info', 'Setup Wizard غیرفعال است یا ربات قبلاً نصب شده است.');
        }

        // اگر اولین بار است و هنوز یوزر/پسورد تنظیم نشده
        if (env('FIRST_RUN', false) && empty(env('ADMIN_USERNAME'))) {
            return redirect()->route('setup.welcome');
        }

        return view('setup.index');
    }

    /**
     * صفحه ایجاد حساب ادمین (اولین بار)
     */
    public function welcome()
    {
        if (!$this->checkWizardAccess()) {
            return redirect()->route('dashboard');
        }

        // اگر قبلاً یوزر تنظیم شده، به صفحه اصلی برو
        if (!empty(env('ADMIN_USERNAME'))) {
            return redirect()->route('setup');
        }

        return view('setup.welcome');
    }

    /**
     * ذخیره اطلاعات ادمین
     */
    public function saveWelcome(Request $request)
    {
        $request->validate([
            'username' => 'required|alpha_dash|min:3|max:20',
            'password' => 'required|min:6|confirmed',
        ], [
            'username.required' => 'نام کاربری الزامی است.',
            'username.alpha_dash' => 'فقط حروف انگلیسی، اعداد و _ مجاز است.',
            'username.min' => 'نام کاربری باید حداقل 3 کاراکتر باشد.',
            'password.required' => 'رمز عبور الزامی است.',
            'password.min' => 'رمز عبور باید حداقل 6 کاراکتر باشد.',
            'password.confirmed' => 'رمزهای عبور مطابقت ندارند.',
        ]);

        // ذخیره در .env
        $envPath = base_path('.env');
        $envContent = file_get_contents($envPath);

        $envContent = preg_replace('/ADMIN_USERNAME=.*/', 'ADMIN_USERNAME=' . $request->username, $envContent);
        $envContent = preg_replace('/ADMIN_PASSWORD=.*/', 'ADMIN_PASSWORD=' . $request->password, $envContent);
        $envContent = preg_replace('/FIRST_RUN=true/', 'FIRST_RUN=false', $envContent);

        file_put_contents($envPath, $envContent);

        // پاک کردن cache
        \Artisan::call('config:clear');

        return redirect()->route('setup')->with('success', 'حساب ادمین با موفقیت ایجاد شد!');
    }

    /**
     * مرحله 0: Import بکاپ (اختیاری)
     */
    public function step0()
    {
        if (!$this->checkWizardAccess()) {
            return redirect()->route('dashboard');
        }

        return view('setup.step0');
    }

    /**
     * مرحله 1: تنظیمات اولیه
     */
    public function step1()
    {
        if (!$this->checkWizardAccess()) {
            return redirect()->route('dashboard');
        }

        return view('setup.step1');
    }

    /**
     * ذخیره مرحله 1
     */
    public function saveStep1(Request $request)
    {
        $request->validate([
            'bot_token' => 'required',
            'bot_username' => 'required',
            'admin_telegram_id' => 'required|numeric',
        ]);

        session([
            'setup_step1' => [
                'bot_token' => $request->bot_token,
                'bot_username' => $request->bot_username,
                'admin_telegram_id' => $request->admin_telegram_id,
            ]
        ]);

        return redirect()->route('setup.step2');
    }

    /**
     * مرحله 2: پنل VPN
     */
    public function step2()
    {
        if (!session('setup_step1')) {
            return redirect()->route('setup.step1');
        }

        return view('setup.step2');
    }

    /**
     * ذخیره مرحله 2
     */
    public function saveStep2(Request $request)
    {
        $request->validate([
            'panel_name' => 'required',
            'panel_type' => 'required|in:marzban,hiddify',
            'panel_url' => 'required|url',
            'panel_username' => 'required',
            'panel_password' => 'required',
        ]);

        session([
            'setup_step2' => [
                'panel_name' => $request->panel_name,
                'panel_type' => $request->panel_type,
                'panel_url' => rtrim($request->panel_url, '/'),
                'panel_username' => $request->panel_username,
                'panel_password' => $request->panel_password,
            ]
        ]);

        return redirect()->route('setup.step3');
    }

    /**
     * مرحله 3: تنظیمات پرداخت
     */
    public function step3()
    {
        if (!session('setup_step2')) {
            return redirect()->route('setup.step2');
        }

        return view('setup.step3');
    }

    /**
     * ذخیره مرحله 3
     */
    public function saveStep3(Request $request)
    {
        session([
            'setup_step3' => [
                'zarinpal_merchant' => $request->zarinpal_merchant ?? '',
                'support_username' => $request->support_username ?? '',
                'channel_id' => $request->channel_id ?? '',
            ]
        ]);

        return redirect()->route('setup.step4');
    }

    /**
     * مرحله 4: خلاصه و نصب
     */
    public function step4()
    {
        if (!session('setup_step3')) {
            return redirect()->route('setup.step3');
        }

        $setup_data = [
            'step1' => session('setup_step1'),
            'step2' => session('setup_step2'),
            'step3' => session('setup_step3'),
        ];

        return view('setup.step4', compact('setup_data'));
    }

    /**
     * اجرای نصب
     */
    public function install(Request $request)
    {
        if (!$this->checkWizardAccess()) {
            return response()->json(['success' => false, 'message' => 'دسترسی غیرمجاز!']);
        }

        try {
            $step1 = session('setup_step1');
            $step2 = session('setup_step2');
            $step3 = session('setup_step3');

            if (!$step1 || !$step2 || !$step3) {
                return response()->json(['success' => false, 'message' => 'اطلاعات ناقص است!']);
            }

            // 1. ایجاد فایل .env ربات
            $this->createBotEnv($step1, $step2, $step3);

            // 2. نصب dependencies ربات
            $this->installBotDependencies();

            // 3. اجرای migrations
            $this->runMigrations();

            // 4. ثبت پنل در دیتابیس
            $this->savePanelToDatabase($step2);

            // 5. ثبت تنظیمات در دیتابیس
            $this->saveSettingsToDatabase($step3);

            // 6. ایجاد systemd service (اختیاری)
            $this->createSystemdService();

            // 7. راه‌اندازی ربات
            $this->startBot();

            // 8. غیرفعال کردن wizard
            $this->disableWizard();

            // پاک کردن session
            session()->forget(['setup_step1', 'setup_step2', 'setup_step3']);

            return response()->json([
                'success' => true,
                'message' => 'نصب با موفقیت انجام شد!',
                'redirect' => route('dashboard')
            ]);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'message' => 'خطا در نصب: ' . $e->getMessage()
            ]);
        }
    }

    /**
     * ایجاد فایل .env ربات
     */
    private function createBotEnv($step1, $step2, $step3)
    {
        $envContent = "# Telegram Bot Configuration\n";
        $envContent .= "TELEGRAM_BOT_TOKEN={$step1['bot_token']}\n";
        $envContent .= "TELEGRAM_BOT_USERNAME={$step1['bot_username']}\n";
        $envContent .= "ADMIN_ID={$step1['admin_telegram_id']}\n\n";

        $envContent .= "# Database\n";
        $envContent .= "DATABASE_URL=sqlite:///" . $this->projectRoot . "/vpn_bot.db\n\n";

        $envContent .= "# Payment Gateway\n";
        $envContent .= "ZARINPAL_MERCHANT_ID={$step3['zarinpal_merchant']}\n\n";

        $envContent .= "# Support & Channel\n";
        $envContent .= "SUPPORT_USERNAME={$step3['support_username']}\n";
        $envContent .= "CHANNEL_LOCK_ID={$step3['channel_id']}\n";

        file_put_contents($this->projectRoot . '/.env', $envContent);
    }

    /**
     * نصب dependencies ربات
     */
    private function installBotDependencies()
    {
        $venvPath = $this->projectRoot . '/venv';

        if (!file_exists($venvPath)) {
            shell_exec("cd {$this->projectRoot} && python3 -m venv venv");
        }

        shell_exec("cd {$this->projectRoot} && source venv/bin/activate && pip install -r requirements.txt 2>&1");
    }

    /**
     * اجرای migrations
     */
    private function runMigrations()
    {
        shell_exec("cd {$this->projectRoot} && source venv/bin/activate && alembic upgrade head 2>&1");
    }

    /**
     * ذخیره پنل در دیتابیس
     */
    private function savePanelToDatabase($panelData)
    {
        $dbPath = $this->projectRoot . '/vpn_bot.db';

        if (!file_exists($dbPath)) {
            throw new \Exception('دیتابیس یافت نشد!');
        }

        $pdo = new \PDO("sqlite:$dbPath");

        $stmt = $pdo->prepare("
            INSERT INTO panels (name, panel_type, api_base_url, username, password, is_active)
            VALUES (:name, :type, :url, :username, :password, 1)
        ");

        $stmt->execute([
            'name' => $panelData['panel_name'],
            'type' => $panelData['panel_type'],
            'url' => $panelData['panel_url'],
            'username' => $panelData['panel_username'],
            'password' => $panelData['panel_password'],
        ]);
    }

    /**
     * ذخیره تنظیمات در دیتابیس
     */
    private function saveSettingsToDatabase($settings)
    {
        $dbPath = $this->projectRoot . '/vpn_bot.db';
        $pdo = new \PDO("sqlite:$dbPath");

        $settingsMap = [
            'zarinpal_merchant_id' => $settings['zarinpal_merchant'],
            'support_username' => $settings['support_username'],
            'channel_id' => $settings['channel_id'],
        ];

        foreach ($settingsMap as $key => $value) {
            if (empty($value)) continue;

            $stmt = $pdo->prepare("
                INSERT OR REPLACE INTO settings (key, value)
                VALUES (:key, :value)
            ");

            $stmt->execute(['key' => $key, 'value' => $value]);
        }
    }

    /**
     * ایجاد systemd service
     */
    private function createSystemdService()
    {
        $serviceContent = "[Unit]\n";
        $serviceContent .= "Description=MeowVPN Telegram Bot\n";
        $serviceContent .= "After=network.target\n\n";
        $serviceContent .= "[Service]\n";
        $serviceContent .= "Type=simple\n";
        $serviceContent .= "User=" . get_current_user() . "\n";
        $serviceContent .= "WorkingDirectory={$this->projectRoot}\n";
        $serviceContent .= "Environment=\"PATH={$this->projectRoot}/venv/bin\"\n";
        $serviceContent .= "ExecStart={$this->projectRoot}/venv/bin/python main.py\n";
        $serviceContent .= "Restart=always\n";
        $serviceContent .= "RestartSec=10\n\n";
        $serviceContent .= "[Install]\n";
        $serviceContent .= "WantedBy=multi-user.target\n";

        file_put_contents('/tmp/meowvpnbot.service', $serviceContent);

        // نصب service (نیاز به sudo دارد)
        shell_exec("sudo mv /tmp/meowvpnbot.service /etc/systemd/system/ 2>&1");
        shell_exec("sudo systemctl daemon-reload 2>&1");
        shell_exec("sudo systemctl enable meowvpnbot 2>&1");
    }

    /**
     * راه‌اندازی ربات
     */
    private function startBot()
    {
        // تلاش برای استفاده از systemd
        $result = shell_exec("sudo systemctl start meowvpnbot 2>&1");

        if (strpos($result, 'Failed') !== false) {
            // اگر systemd کار نکرد، background اجرا کن
            shell_exec("cd {$this->projectRoot} && nohup venv/bin/python main.py > bot.log 2>&1 &");
        }
    }

    /**
     * غیرفعال کردن wizard
     */
    private function disableWizard()
    {
        // به‌روزرسانی .env
        $envPath = base_path('.env');
        $envContent = file_get_contents($envPath);

        $envContent = preg_replace('/SETUP_WIZARD_ENABLED=true/', 'SETUP_WIZARD_ENABLED=false', $envContent);
        $envContent = preg_replace('/BOT_INSTALLED=false/', 'BOT_INSTALLED=true', $envContent);

        file_put_contents($envPath, $envContent);

        // پاک کردن کش
        Artisan::call('config:clear');
        Artisan::call('cache:clear');
    }
}

