<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class DisableSetupWizard extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'setup:disable';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'غیرفعال کردن Setup Wizard بعد از نصب';

    /**
     * Execute the console command.
     *
     * @return int
     */
    public function handle()
    {
        $envFile = base_path('.env');

        if (!file_exists($envFile)) {
            $this->error('.env فایل یافت نشد!');
            return 1;
        }

        // خواندن فایل .env
        $envContent = file_get_contents($envFile);

        // به‌روزرسانی متغیرها
        $envContent = preg_replace(
            '/SETUP_WIZARD_ENABLED=.*/',
            'SETUP_WIZARD_ENABLED=false',
            $envContent
        );

        // ذخیره فایل
        file_put_contents($envFile, $envContent);

        // پاک کردن cache
        $this->call('config:clear');
        $this->call('cache:clear');
        $this->call('config:cache');

        $this->info('✓ Setup Wizard غیرفعال شد');
        $this->info('✓ سایت آماده استفاده است');

        return 0;
    }
}

