<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Artisan;

class SetupWizardController extends Controller
{
    private $projectRoot;

    public function __construct()
    {
        $basePath = base_path();
        
        // اولویت اول: مسیر استاندارد نصب (/var/www/meowvpnbot)
        $standardPath = '/var/www/meowvpnbot';
        if (is_dir($standardPath) && file_exists($standardPath . '/main.py')) {
            $this->projectRoot = $standardPath;
            \Log::info("SetupWizard: Using standard installation path: {$standardPath}");
            return;
        }

        // اولویت دوم: تشخیص خودکار از مسیر فعلی
        // اگر در site هستیم، یک سطح بالا برو
        if (strpos($basePath, '/site') !== false) {
            $this->projectRoot = dirname($basePath);
        } else {
        $this->projectRoot = base_path('..');
        }

        // بررسی صحت مسیر تشخیص داده شده
        if (is_dir($this->projectRoot) && file_exists($this->projectRoot . '/main.py')) {
            \Log::info("SetupWizard: Found project root at: {$this->projectRoot}");
            return;
        }

        // اولویت سوم: جستجو در مسیرهای ممکن
            $possiblePaths = [
            '/var/www/meowvpnbot',  // مسیر استاندارد (دوباره چک می‌شود برای اطمینان)
            dirname($basePath),      // یک سطح بالا از base_path
            base_path('..'),         // یک سطح بالا (relative)
            realpath(base_path('..')), // یک سطح بالا (absolute)
            ];

        // اضافه کردن مسیرهای خاص توسعه (فقط برای محیط توسعه)
        if (strpos($basePath, '/mnt/') !== false || strpos($basePath, '/home/') !== false) {
            $possiblePaths[] = dirname($basePath);
            // اگر در پوشه site هستیم، یک سطح بالاتر
            if (basename($basePath) === 'site') {
                $possiblePaths[] = dirname($basePath);
            }
        }

            foreach ($possiblePaths as $path) {
                if ($path && is_dir($path) && file_exists($path . '/main.py')) {
                    $this->projectRoot = $path;
                    \Log::info("SetupWizard: Found project root at: {$path}");
                return;
            }
        }

        // اگر هنوز پیدا نشد، استفاده از مسیر استاندارد به عنوان fallback
        // حتی اگر فایل main.py وجود نداشته باشد (برای نصب اولیه)
        if (is_dir($standardPath)) {
            $this->projectRoot = $standardPath;
            \Log::warning("SetupWizard: Using standard path as fallback (main.py may not exist yet): {$standardPath}");
        } else {
            \Log::warning("SetupWizard: مسیر پروژه یافت نشد. base_path: {$basePath}, projectRoot: {$this->projectRoot}");
        }
    }

    /**
     * بررسی دسترسی به Setup Wizard
     */
    private function checkWizardAccess()
    {
        // اگر admin نساخته شده، همیشه دسترسی بده
        if (empty(env('ADMIN_USERNAME'))) {
            return true;
        }

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
        // اگر admin نساخته نشده، به welcome برو
        if (empty(env('ADMIN_USERNAME'))) {
            return redirect()->route('setup.welcome');
        }

        // اگر wizard غیرفعال است یا ربات نصب شده
        if (!env('SETUP_WIZARD_ENABLED', false) || env('BOT_INSTALLED', false)) {
            // اگر لاگین کرده، به dashboard برو
            if (session()->has('user_authenticated')) {
                return redirect()->route('dashboard');
            }
            // اگر لاگین نکرده، به login برو
            return redirect()->route('login');
        }

        return view('setup.index');
    }

    /**
     * صفحه ایجاد حساب ادمین (اولین بار)
     */
    public function welcome()
    {
        // فقط صفحه welcome رو نشون بده - بدون redirect
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

        // بررسی وجود فایل
        if (!file_exists($envPath)) {
            return back()->withErrors(['username' => 'فایل .env یافت نشد!'])->withInput();
        }

        // خواندن محتوا
        $envContent = file_get_contents($envPath);
        if ($envContent === false) {
            return back()->withErrors(['username' => 'خطا در خواندن فایل .env!'])->withInput();
        }

        // Hash کردن password قبل از ذخیره
        $hashedPassword = password_hash($request->password, PASSWORD_DEFAULT);

        $usernameEscaped = addslashes($request->username);
        $passwordEscaped = addslashes($hashedPassword);

        $envContent = preg_replace('/ADMIN_USERNAME=.*/', 'ADMIN_USERNAME=' . $usernameEscaped, $envContent);
        $envContent = preg_replace('/ADMIN_PASSWORD=.*/', 'ADMIN_PASSWORD=' . $passwordEscaped, $envContent);

        // اگر متغیر وجود نداشت، اضافه کن
        if (strpos($envContent, 'ADMIN_USERNAME=') === false) {
            $envContent .= "\nADMIN_USERNAME={$usernameEscaped}\n";
        }
        if (strpos($envContent, 'ADMIN_PASSWORD=') === false) {
            $envContent .= "\nADMIN_PASSWORD={$passwordEscaped}\n";
        }

        $envContent = preg_replace('/FIRST_RUN=true/', 'FIRST_RUN=false', $envContent);

        // نوشتن با بررسی مجوز
        $result = @file_put_contents($envPath, $envContent);
        if ($result === false) {
            // اگر نوشتن با خطا مواجه شد، با sudo امتحان کن
            $tempFile = sys_get_temp_dir() . '/env_update_' . uniqid();
            file_put_contents($tempFile, $envContent);
            $tempFileEscaped = escapeshellarg($tempFile);
            $envPathEscaped = escapeshellarg($envPath);
            exec("sudo mv {$tempFileEscaped} {$envPathEscaped} 2>&1", $output, $returnCode);
            if ($returnCode !== 0) {
                return back()->withErrors(['username' => 'خطا در نوشتن فایل .env! لطفاً مجوزها را بررسی کنید.'])->withInput();
            }
        }

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
            'bot_token' => [
                'required',
                'regex:/^\d+:[A-Za-z0-9_-]+$/',
            ],
            'bot_username' => [
                'required',
                'regex:/^[a-zA-Z0-9_]+$/',
                'min:3',
                'max:32',
            ],
            'admin_telegram_id' => [
                'required',
                'numeric',
                'min:1',
            ],
        ], [
            'bot_token.required' => 'توکن ربات الزامی است.',
            'bot_token.regex' => 'فرمت توکن ربات نامعتبر است. فرمت صحیح: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
            'bot_username.required' => 'یوزرنیم ربات الزامی است.',
            'bot_username.regex' => 'یوزرنیم ربات باید فقط شامل حروف انگلیسی، اعداد و _ باشد.',
            'bot_username.min' => 'یوزرنیم ربات باید حداقل 3 کاراکتر باشد.',
            'bot_username.max' => 'یوزرنیم ربات نباید بیشتر از 32 کاراکتر باشد.',
            'admin_telegram_id.required' => 'Telegram ID ادمین الزامی است.',
            'admin_telegram_id.numeric' => 'Telegram ID باید عدد باشد.',
            'admin_telegram_id.min' => 'Telegram ID باید بزرگتر از 0 باشد.',
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
        $request->validate([
            'zarinpal_merchant' => [
                'nullable',
                'regex:/^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/i',
            ],
            'support_username' => [
                'nullable',
                'regex:/^[a-zA-Z0-9_]+$/',
                'max:32',
            ],
            'channel_id' => [
                'nullable',
                'regex:/^@?[a-zA-Z0-9_]+$/',
                'max:100',
            ],
        ], [
            'zarinpal_merchant.regex' => 'فرمت Merchant ID زرین‌پال نامعتبر است. فرمت صحیح: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx',
            'support_username.regex' => 'یوزرنیم پشتیبانی باید فقط شامل حروف انگلیسی، اعداد و _ باشد.',
            'support_username.max' => 'یوزرنیم پشتیبانی نباید بیشتر از 32 کاراکتر باشد.',
            'channel_id.regex' => 'آیدی کانال نامعتبر است. می‌تواند با @ شروع شود یا بدون آن.',
            'channel_id.max' => 'آیدی کانال نباید بیشتر از 100 کاراکتر باشد.',
        ]);

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
            \Log::info('Setup Wizard Install Started', [
                'project_root' => $this->projectRoot ?? 'not set',
                'has_step1' => !empty(session('setup_step1')),
                'has_step2' => !empty(session('setup_step2')),
                'has_step3' => !empty(session('setup_step3')),
            ]);

            $step1 = session('setup_step1');
            $step2 = session('setup_step2');
            $step3 = session('setup_step3');

            if (!$step1 || !$step2 || !$step3) {
                \Log::warning('Setup Wizard: Missing steps', [
                    'step1' => !empty($step1),
                    'step2' => !empty($step2),
                    'step3' => !empty($step3),
                ]);
                return response()->json(['success' => false, 'message' => 'اطلاعات ناقص است! لطفاً مراحل قبلی را تکمیل کنید.']);
            }

            // بررسی مسیر پروژه
            if (empty($this->projectRoot) || !is_dir($this->projectRoot)) {
                $errorMsg = "مسیر پروژه یافت نشد: " . ($this->projectRoot ?? 'تعیین نشده') . ". لطفاً مسیر نصب را بررسی کنید.";
                \Log::error('Setup Wizard: Project root not found', ['project_root' => $this->projectRoot]);
                throw new \Exception($errorMsg);
            }

            \Log::info('Setup Wizard: Creating storage directories');
            // 0. ایجاد پوشه‌های storage (اگر وجود ندارند)
            $this->createStorageDirectories();
            \Log::info('Setup Wizard: Storage directories created');

            \Log::info('Setup Wizard: Creating bot .env file');
            // 1. ایجاد فایل .env ربات
            $this->createBotEnv($step1, $step2, $step3);
            \Log::info('Setup Wizard: Bot .env file created');

            \Log::info('Setup Wizard: Updating Laravel .env with bot database path');
            // 1.5. به‌روزرسانی Laravel .env با مسیر دیتابیس ربات
            $this->updateLaravelEnvWithBotDatabasePath();
            \Log::info('Setup Wizard: Laravel .env updated');

            \Log::info('Setup Wizard: Installing bot dependencies');
            // 2. نصب dependencies ربات
            $this->installBotDependencies();
            \Log::info('Setup Wizard: Bot dependencies installed');

            \Log::info('Setup Wizard: Running migrations');
            // 3. اجرای migrations
            $this->runMigrations();
            \Log::info('Setup Wizard: Migrations completed');

            // تنظیم مجوزهای دیتابیس پس از migrations
            $dbPath = $this->projectRoot . '/vpn_bot.db';
            if (file_exists($dbPath)) {
                $this->setDatabasePermissions($dbPath);
            }

            \Log::info('Setup Wizard: Saving panel to database');
            // 4. ثبت پنل در دیتابیس
            $this->savePanelToDatabase($step2);
            \Log::info('Setup Wizard: Panel saved');

            \Log::info('Setup Wizard: Saving settings to database');
            // 5. ثبت تنظیمات در دیتابیس
            $this->saveSettingsToDatabase($step3);
            \Log::info('Setup Wizard: Settings saved');

            \Log::info('Setup Wizard: Creating systemd service');
            // 6. ایجاد systemd service (اختیاری)
            try {
                $this->createSystemdService();
                \Log::info('Setup Wizard: Systemd service created');
            } catch (\Exception $e) {
                \Log::warning('Setup Wizard: Failed to create systemd service', ['error' => $e->getMessage()]);
                // ادامه بده حتی اگر systemd service ایجاد نشد
            }

            \Log::info('Setup Wizard: Starting bot');
            // 7. راه‌اندازی ربات
            try {
                $this->startBot();
                \Log::info('Setup Wizard: Bot started');
            } catch (\Exception $e) {
                \Log::warning('Setup Wizard: Failed to start bot', ['error' => $e->getMessage()]);
                // ادامه بده حتی اگر ربات راه‌اندازی نشد
            }

            \Log::info('Setup Wizard: Disabling wizard');
            // 8. غیرفعال کردن wizard
            $this->disableWizard();
            \Log::info('Setup Wizard: Wizard disabled');

            // پاک کردن session
            session()->forget(['setup_step1', 'setup_step2', 'setup_step3']);

            return response()->json([
                'success' => true,
                'message' => 'نصب با موفقیت انجام شد!',
                'redirect' => route('dashboard')
            ]);

        } catch (\Exception $e) {
            // لاگ کردن خطا برای دیباگ
            $errorDetails = [
                'message' => $e->getMessage(),
                'file' => $e->getFile(),
                'line' => $e->getLine(),
                'project_root' => $this->projectRoot ?? 'not set',
                'trace' => $e->getTraceAsString()
            ];

            \Log::error('Setup Wizard Install Error', $errorDetails);

            // ساخت پیام خطای کاربرپسند
            $userMessage = 'خطا در نصب: ' . $e->getMessage();

            // اگر خطا مربوط به مجوزها باشد، راهنمایی بده
            if (strpos($e->getMessage(), 'مجوز') !== false || strpos($e->getMessage(), 'permission') !== false) {
                $userMessage .= "\n\nراه حل: لطفاً مجوزهای مسیر پروژه را بررسی کنید:\nsudo chown -R www-data:www-data " . ($this->projectRoot ?? '/var/www/meowvpnbot');
            }

            // اگر خطا مربوط به مسیر باشد، راهنمایی بده
            if (strpos($e->getMessage(), 'مسیر') !== false || strpos($e->getMessage(), 'path') !== false) {
                $userMessage .= "\n\nراه حل: لطفاً مسیر نصب را بررسی کنید. مسیر فعلی: " . ($this->projectRoot ?? 'تعیین نشده');
            }

            return response()->json([
                'success' => false,
                'message' => $userMessage,
                'error_code' => $e->getCode(),
                'error_details' => config('app.debug') ? [
                    'file' => basename($e->getFile()),
                    'line' => $e->getLine(),
                    'project_root' => $this->projectRoot ?? 'not set',
                ] : null
            ], 500);
        }
    }

    /**
     * ایجاد پوشه‌های storage برای Laravel
     */
    private function createStorageDirectories()
    {
        $siteDir = base_path();
        $storageDir = $siteDir . '/storage';
        $logsDir = $storageDir . '/logs';
        $frameworkDir = $storageDir . '/framework';
        $sessionsDir = $frameworkDir . '/sessions';
        $viewsDir = $frameworkDir . '/views';
        $cacheDir = $frameworkDir . '/cache';
        $bootstrapCacheDir = $siteDir . '/bootstrap/cache';

        // ایجاد پوشه‌ها
        $directories = [
            $logsDir,
            $sessionsDir,
            $viewsDir,
            $cacheDir,
            $bootstrapCacheDir,
        ];

        foreach ($directories as $dir) {
            if (!is_dir($dir)) {
                if (!@mkdir($dir, 0775, true)) {
                    \Log::warning("Setup Wizard: Failed to create directory: {$dir}");
                    // سعی کن با sudo
                    $dirEscaped = escapeshellarg($dir);
                    $output = shell_exec("sudo mkdir -p {$dirEscaped} 2>&1");
                    if (!is_dir($dir)) {
                        throw new \Exception("نمی‌توان پوشه را ایجاد کرد: {$dir}");
                    }
                }
            }
        }

        // تنظیم مجوزها
        $chmodDirs = [$storageDir, $bootstrapCacheDir];
        foreach ($chmodDirs as $dir) {
            if (is_dir($dir)) {
                @chmod($dir, 0775);
                // سعی کن با sudo
                $dirEscaped = escapeshellarg($dir);
                shell_exec("sudo chmod -R 775 {$dirEscaped} 2>&1");
            }
        }

        // تنظیم مالکیت
        $user = 'www-data';
        if (!shell_exec("id {$user} 2>&1")) {
            $user = 'nginx';
        }

        if (shell_exec("id {$user} 2>&1")) {
            foreach ($chmodDirs as $dir) {
                if (is_dir($dir)) {
                    $dirEscaped = escapeshellarg($dir);
                    shell_exec("sudo chown -R {$user}:{$user} {$dirEscaped} 2>&1");
                }
            }
        }

        // ایجاد فایل .gitkeep
        $gitkeepFiles = [
            $logsDir . '/.gitkeep',
            $sessionsDir . '/.gitkeep',
            $viewsDir . '/.gitkeep',
            $cacheDir . '/.gitkeep',
            $bootstrapCacheDir . '/.gitkeep',
        ];

        foreach ($gitkeepFiles as $file) {
            if (!file_exists($file)) {
                @file_put_contents($file, '');
            }
        }

        \Log::info('Setup Wizard: Storage directories created successfully', [
            'storage_dir' => $storageDir,
            'logs_dir' => $logsDir,
        ]);
    }

    /**
     * ایجاد فایل .env ربات
     */
    private function createBotEnv($step1, $step2, $step3)
    {
        // بررسی وجود مسیر پروژه
        if (!is_dir($this->projectRoot)) {
            throw new \Exception("مسیر پروژه یافت نشد: {$this->projectRoot}");
        }

        // Escape کردن مقادیر برای .env
        $botToken = addslashes($step1['bot_token']);
        $botUsername = addslashes($step1['bot_username']);
        $adminId = (int)$step1['admin_telegram_id'];
        $zarinpalMerchant = addslashes($step3['zarinpal_merchant'] ?? '');
        $supportUsername = addslashes($step3['support_username'] ?? '');
        $channelId = addslashes($step3['channel_id'] ?? '');

        $envContent = "# Telegram Bot Configuration\n";
        $envContent .= "TELEGRAM_BOT_TOKEN={$botToken}\n";
        $envContent .= "TELEGRAM_BOT_USERNAME={$botUsername}\n";
        $envContent .= "ADMIN_ID={$adminId}\n";
        $envContent .= "ADMIN_IDS={$adminId}\n\n";

        $envContent .= "# Database\n";
        $dbPath = str_replace('\\', '/', $this->projectRoot . '/vpn_bot.db');
        $envContent .= "DATABASE_URL=sqlite:///{$dbPath}\n\n";

        $envContent .= "# Payment Gateway\n";
        if (!empty($zarinpalMerchant)) {
            $envContent .= "ZARINPAL_MERCHANT_ID={$zarinpalMerchant}\n\n";
        } else {
            $envContent .= "ZARINPAL_MERCHANT_ID=\n\n";
        }

        $envContent .= "# Support & Channel\n";
        if (!empty($supportUsername)) {
            $envContent .= "SUPPORT_USERNAME={$supportUsername}\n";
        } else {
            $envContent .= "SUPPORT_USERNAME=\n";
        }
        if (!empty($channelId)) {
            $envContent .= "CHANNEL_LOCK_ID={$channelId}\n";
        } else {
            $envContent .= "CHANNEL_LOCK_ID=\n";
        }

        $envFilePath = $this->projectRoot . '/.env';

        // بررسی مجوز نوشتن
        if (!is_writable(dirname($envFilePath)) && !is_writable($this->projectRoot)) {
            throw new \Exception('مسیر پروژه قابل نوشتن نیست! لطفاً مجوزها را بررسی کنید: ' . $this->projectRoot);
        }

        $result = @file_put_contents($envFilePath, $envContent);
        if ($result === false) {
            // اگر نوشتن با خطا مواجه شد، با sudo امتحان کن
            $tempFile = sys_get_temp_dir() . '/bot_env_' . uniqid();
            if (file_put_contents($tempFile, $envContent) !== false) {
                $tempFileEscaped = escapeshellarg($tempFile);
                $envPathEscaped = escapeshellarg($envFilePath);
                exec("sudo mv {$tempFileEscaped} {$envPathEscaped} 2>&1", $output, $returnCode);
                if ($returnCode !== 0) {
                    throw new \Exception('خطا در نوشتن فایل .env ربات! لطفاً مجوزها را بررسی کنید. خطا: ' . implode(' ', $output));
                }
            } else {
                throw new \Exception('خطا در نوشتن فایل .env ربات! لطفاً مجوزها را بررسی کنید.');
            }
        }
    }

    /**
     * به‌روزرسانی Laravel .env با مسیر دیتابیس ربات
     */
    private function updateLaravelEnvWithBotDatabasePath()
    {
        $laravelEnvPath = base_path('.env');
        $botDbPath = str_replace('\\', '/', $this->projectRoot . '/vpn_bot.db');

        // بررسی وجود فایل .env Laravel
        if (!file_exists($laravelEnvPath)) {
            \Log::warning('Setup Wizard: Laravel .env file not found, skipping BOT_DATABASE_PATH update');
            return;
        }

        // خواندن محتوای فایل
        $envContent = file_get_contents($laravelEnvPath);
        if ($envContent === false) {
            \Log::warning('Setup Wizard: Failed to read Laravel .env file');
            return;
        }

        // بررسی وجود BOT_DATABASE_PATH
        if (preg_match('/^BOT_DATABASE_PATH=.*$/m', $envContent)) {
            // به‌روزرسانی مقدار موجود
            $envContent = preg_replace(
                '/^BOT_DATABASE_PATH=.*$/m',
                'BOT_DATABASE_PATH=' . $botDbPath,
                $envContent
            );
        } else {
            // اضافه کردن BOT_DATABASE_PATH اگر وجود نداشت
            // اضافه کردن بعد از خط خالی یا در انتهای فایل
            if (substr(trim($envContent), -1) !== "\n") {
                $envContent .= "\n";
            }
            $envContent .= "\n# Bot Database Path (برای دسترسی Laravel به دیتابیس ربات)\n";
            $envContent .= "BOT_DATABASE_PATH={$botDbPath}\n";
        }

        // نوشتن فایل
        $result = @file_put_contents($laravelEnvPath, $envContent);
        if ($result === false) {
            // اگر نوشتن با خطا مواجه شد، با sudo امتحان کن
            $tempFile = sys_get_temp_dir() . '/laravel_env_' . uniqid();
            if (file_put_contents($tempFile, $envContent) !== false) {
                $tempFileEscaped = escapeshellarg($tempFile);
                $envPathEscaped = escapeshellarg($laravelEnvPath);
                exec("sudo mv {$tempFileEscaped} {$envPathEscaped} 2>&1", $output, $returnCode);
                if ($returnCode !== 0) {
                    \Log::warning('Setup Wizard: Failed to update Laravel .env with BOT_DATABASE_PATH', [
                        'error' => implode(' ', $output)
                    ]);
                }
            } else {
                \Log::warning('Setup Wizard: Failed to write Laravel .env file');
            }
        }

        // پاک کردن کش Laravel برای اعمال تغییرات
        try {
            Artisan::call('config:clear');
        } catch (\Exception $e) {
            \Log::warning('Setup Wizard: Failed to clear Laravel config cache', ['error' => $e->getMessage()]);
        }
    }

    /**
     * نصب dependencies ربات
     */
    private function installBotDependencies()
    {
        $venvPath = $this->projectRoot . '/venv';
        $projectRootEscaped = escapeshellarg($this->projectRoot);

        if (!file_exists($venvPath)) {
            $venvPathEscaped = escapeshellarg($venvPath);
            $output = shell_exec("cd {$projectRootEscaped} && python3 -m venv {$venvPathEscaped} 2>&1");
            if (!file_exists($venvPath . '/bin/python')) {
                throw new \Exception("خطا در ایجاد virtual environment: " . ($output ?: 'خطای نامشخص'));
            }
        }

        // استفاده مستقیم از venv/bin/pip به جای source activate
        $pipPath = $venvPath . '/bin/pip';
        if (!file_exists($pipPath)) {
            throw new \Exception("pip در virtual environment یافت نشد!");
        }

        $output = shell_exec("cd {$projectRootEscaped} && {$pipPath} install -r requirements.txt 2>&1");
        if ($output && (strpos($output, 'ERROR') !== false || strpos($output, 'error') !== false)) {
            // اگر خطای جدی وجود دارد، throw exception
            if (strpos($output, 'No such file') !== false || strpos($output, 'Permission denied') !== false) {
                throw new \Exception("خطا در نصب dependencies: " . $output);
            }
        }
    }

    /**
     * اجرای migrations
     */
    private function runMigrations()
    {
        $venvPath = $this->projectRoot . '/venv';
        $alembicPath = $venvPath . '/bin/alembic';
        $projectRootEscaped = escapeshellarg($this->projectRoot);

        if (!file_exists($alembicPath)) {
            // اگر alembic نصب نشده، سعی کن نصب کنی
            $pipPath = $venvPath . '/bin/pip';
            if (file_exists($pipPath)) {
                shell_exec("cd {$projectRootEscaped} && {$pipPath} install alembic 2>&1");
            }
        }

        if (!file_exists($alembicPath)) {
            // اگر هنوز نیست، دیتابیس را با create_database.py بساز
            $createDbPath = $this->projectRoot . '/create_database.py';
            if (file_exists($createDbPath)) {
                $pythonPath = $venvPath . '/bin/python';
                $output = shell_exec("cd {$projectRootEscaped} && {$pythonPath} create_database.py 2>&1");
                if ($output && strpos($output, 'ERROR') !== false) {
                    throw new \Exception("خطا در ایجاد دیتابیس: " . $output);
                }
            }
            return; // اگر alembic نیست، از create_database استفاده کردیم
        }

        $output = shell_exec("cd {$projectRootEscaped} && {$alembicPath} upgrade head 2>&1");
        if ($output && (strpos($output, 'ERROR') !== false || strpos($output, 'error') !== false)) {
            // اگر خطای جدی وجود دارد
            if (strpos($output, 'No such file') !== false || strpos($output, 'Permission denied') !== false) {
                throw new \Exception("خطا در اجرای migrations: " . $output);
            }
        }
    }

    /**
     * ذخیره پنل در دیتابیس
     */
    private function savePanelToDatabase($panelData)
    {
        $dbPath = $this->projectRoot . '/vpn_bot.db';

        // بررسی وجود دیتابیس - اگر وجود نداشت، ایجاد کن
        if (!file_exists($dbPath)) {
            // سعی کن دیتابیس را با create_database.py ایجاد کنی
            $createDbPath = $this->projectRoot . '/create_database.py';
            if (file_exists($createDbPath)) {
                $venvPath = $this->projectRoot . '/venv';
                $pythonPath = $venvPath . '/bin/python';
                if (file_exists($pythonPath)) {
                    $projectRootEscaped = escapeshellarg($this->projectRoot);
                    $pythonPathEscaped = escapeshellarg($pythonPath);
                    $output = shell_exec("cd {$projectRootEscaped} && {$pythonPathEscaped} create_database.py 2>&1");
                    if (!file_exists($dbPath)) {
                        throw new \Exception('خطا در ایجاد دیتابیس: ' . ($output ?: 'خطای نامشخص'));
                    }
                } else {
                    throw new \Exception('Python در venv یافت نشد! لطفاً ابتدا dependencies را نصب کنید.');
                }
            } else {
                throw new \Exception('دیتابیس یافت نشد و create_database.py نیز موجود نیست!');
            }
        }

        $pdo = new \PDO("sqlite:$dbPath");
        $pdo->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);

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

        // تنظیم مجوزهای دیتابیس برای دسترسی Laravel
        $this->setDatabasePermissions($dbPath);
    }

    /**
     * تنظیم مجوزهای دیتابیس برای دسترسی Laravel
     */
    private function setDatabasePermissions($dbPath)
    {
        if (!file_exists($dbPath)) {
            return;
        }

        // تعیین کاربر وب سرور
        $webUser = 'www-data';
        if (!posix_getpwnam($webUser)) {
            $webUser = 'nginx';
        }

        // تنظیم مالکیت و مجوزها
        $dbPathEscaped = escapeshellarg($dbPath);
        $output = shell_exec("sudo chown {$webUser}:{$webUser} {$dbPathEscaped} 2>&1");
        $output = shell_exec("sudo chmod 664 {$dbPathEscaped} 2>&1");

        \Log::info('Setup Wizard: Database permissions set', [
            'path' => $dbPath,
            'user' => $webUser
        ]);
    }

    /**
     * ذخیره تنظیمات در دیتابیس
     */
    private function saveSettingsToDatabase($settings)
    {
        $dbPath = $this->projectRoot . '/vpn_bot.db';

        // بررسی وجود دیتابیس
        if (!file_exists($dbPath)) {
            throw new \Exception('دیتابیس یافت نشد! لطفاً ابتدا migrations را اجرا کنید.');
        }

        // استفاده از PDO مستقیم در Setup Wizard (قبل از تنظیم env variables)
        $pdo = new \PDO("sqlite:$dbPath");
        $pdo->setAttribute(\PDO::ATTR_ERRMODE, \PDO::ERRMODE_EXCEPTION);

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

        // تنظیم مجوزهای دیتابیس پس از ذخیره تنظیمات
        $this->setDatabasePermissions($dbPath);
    }

    /**
     * ایجاد systemd service
     */
    private function createSystemdService()
    {
        // پیدا کردن python executable در venv
        $pythonPath = $this->projectRoot . '/venv/bin/python';
        if (!file_exists($pythonPath)) {
            $pythonPath = $this->projectRoot . '/venv/bin/python3';
        }
        if (!file_exists($pythonPath)) {
            throw new \Exception("Python در venv یافت نشد!");
        }

        $projectRootEscaped = escapeshellarg($this->projectRoot);
        $pythonPathEscaped = escapeshellarg($pythonPath);
        $mainPyEscaped = escapeshellarg($this->projectRoot . '/main.py');

        // استفاده از www-data به جای get_current_user
        $serviceUser = 'www-data';
        // اگر www-data وجود ندارد، از کاربر فعلی استفاده کن
        if (!posix_getpwnam($serviceUser)) {
            $serviceUser = get_current_user();
        }

        $serviceContent = "[Unit]\n";
        $serviceContent .= "Description=MeowVPN Telegram Bot\n";
        $serviceContent .= "After=network.target\n\n";
        $serviceContent .= "[Service]\n";
        $serviceContent .= "Type=simple\n";
        $serviceContent .= "User={$serviceUser}\n";
        $serviceContent .= "WorkingDirectory={$projectRootEscaped}\n";
        $serviceContent .= "Environment=\"PATH={$projectRootEscaped}/venv/bin\"\n";
        $serviceContent .= "ExecStart={$pythonPathEscaped} {$mainPyEscaped}\n";
        $serviceContent .= "Restart=always\n";
        $serviceContent .= "RestartSec=10\n";
        $serviceContent .= "StartLimitInterval=0\n";
        $serviceContent .= "StartLimitBurst=10\n\n";
        $serviceContent .= "[Install]\n";
        $serviceContent .= "WantedBy=multi-user.target\n";

        $serviceFile = '/tmp/meowvpn-bot.service';
        $result = @file_put_contents($serviceFile, $serviceContent);
        if ($result === false) {
            throw new \Exception("خطا در ایجاد فایل systemd service! لطفاً مجوزها را بررسی کنید.");
        }

        // نصب service (نیاز به sudo دارد)
        $serviceFileEscaped = escapeshellarg($serviceFile);
        $output = shell_exec("sudo mv {$serviceFileEscaped} /etc/systemd/system/meowvpn-bot.service 2>&1");
        if ($output && strpos($output, 'Permission denied') !== false) {
            throw new \Exception("خطا در نصب systemd service: " . $output);
        }

        $output = shell_exec("sudo systemctl daemon-reload 2>&1");
        if ($output && strpos($output, 'Failed') !== false) {
            throw new \Exception("خطا در reload systemd: " . $output);
        }

        $output = shell_exec("sudo systemctl enable meowvpn-bot.service 2>&1");
        if ($output && strpos($output, 'Failed') !== false) {
            throw new \Exception("خطا در enable کردن سرویس: " . $output);
        }
    }

    /**
     * راه‌اندازی ربات
     */
    private function startBot()
    {
        $projectRootEscaped = escapeshellarg($this->projectRoot);
        $pythonPath = escapeshellarg($this->projectRoot . '/venv/bin/python');
        $mainPyPath = escapeshellarg($this->projectRoot . '/main.py');

        // تلاش برای استفاده از systemd
        $output = shell_exec("sudo systemctl start meowvpn-bot.service 2>&1");

        if ($output && (strpos($output, 'Failed') !== false || strpos($output, 'not found') !== false)) {
            // اگر systemd کار نکرد، background اجرا کن
            $logFile = escapeshellarg($this->projectRoot . '/bot.log');
            $output = shell_exec("cd {$projectRootEscaped} && nohup {$pythonPath} {$mainPyPath} > {$logFile} 2>&1 &");
            if ($output && strpos($output, 'Permission denied') !== false) {
                throw new \Exception("خطا در راه‌اندازی ربات: " . $output);
            }
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

        $result = @file_put_contents($envPath, $envContent);
        if ($result === false) {
            // اگر نوشتن با خطا مواجه شد، با sudo امتحان کن
            $tempFile = sys_get_temp_dir() . '/env_update_' . uniqid();
            file_put_contents($tempFile, $envContent);
            $tempFileEscaped = escapeshellarg($tempFile);
            $envPathEscaped = escapeshellarg($envPath);
            exec("sudo mv {$tempFileEscaped} {$envPathEscaped} 2>&1", $output, $returnCode);
            if ($returnCode !== 0) {
                throw new \Exception('خطا در نوشتن فایل .env! لطفاً مجوزها را بررسی کنید.');
            }
        }

        // پاک کردن کش
        Artisan::call('config:clear');
        Artisan::call('cache:clear');
    }
}

