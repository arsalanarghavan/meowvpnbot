<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\SetupWizardController;
use App\Http\Controllers\BackupImportController;
use App\Http\Controllers\DashboardController;
use App\Http\Controllers\UserController;
use App\Http\Controllers\ServiceController;
use App\Http\Controllers\PlanController;
use App\Http\Controllers\PanelController;
use App\Http\Controllers\TransactionController;
use App\Http\Controllers\MarketerController;
use App\Http\Controllers\GiftCardController;
use App\Http\Controllers\CardAccountController;
use App\Http\Controllers\SettingController;

// Setup Wizard (بدون middleware - فقط اگر فعال باشد)
Route::prefix('setup')->group(function () {
    Route::get('/', [SetupWizardController::class, 'index'])->name('setup');
    Route::get('/welcome', [SetupWizardController::class, 'welcome'])->name('setup.welcome');
    Route::post('/welcome', [SetupWizardController::class, 'saveWelcome'])->name('setup.welcome.save');
    Route::get('/step0', [BackupImportController::class, 'index'])->name('setup.step0');
    Route::get('/step1', [SetupWizardController::class, 'step1'])->name('setup.step1');
    Route::post('/step1', [SetupWizardController::class, 'saveStep1'])->name('setup.step1.save');
    Route::get('/step2', [SetupWizardController::class, 'step2'])->name('setup.step2');
    Route::post('/step2', [SetupWizardController::class, 'saveStep2'])->name('setup.step2.save');
    Route::get('/step3', [SetupWizardController::class, 'step3'])->name('setup.step3');
    Route::post('/step3', [SetupWizardController::class, 'saveStep3'])->name('setup.step3.save');
    Route::get('/step4', [SetupWizardController::class, 'step4'])->name('setup.step4');
    Route::post('/install', [SetupWizardController::class, 'install'])->name('setup.install');
});

// Backup Import Routes
Route::prefix('backup')->group(function () {
    Route::post('/analyze', [BackupImportController::class, 'analyze'])->name('backup.analyze');
    Route::post('/import', [BackupImportController::class, 'import'])->name('backup.import');
    Route::get('/sample', [BackupImportController::class, 'downloadSample'])->name('backup.sample');
});

// Root redirect
Route::get('/', function () {
    // اگر admin نساخته شده، به welcome برو
    if (empty(env('ADMIN_USERNAME'))) {
        return redirect()->route('setup.welcome');
    }
    
    // اگر wizard فعال است و bot نصب نشده
    if (env('SETUP_WIZARD_ENABLED', false) && !env('BOT_INSTALLED', false)) {
        // اگر لاگین کرده، به setup برو
        if (session()->has('user_authenticated')) {
            return redirect()->route('setup');
        }
        // اگر لاگین نکرده، به welcome برو
        return redirect()->route('setup.welcome');
    }
    
    // اگر لاگین کرده، به dashboard برو
    if (session()->has('user_authenticated')) {
        return redirect()->route('dashboard');
    }
    
    // در غیر این صورت به login برو
    return redirect()->route('login');
});

// صفحات احراز هویت (بدون middleware)
Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
Route::post('/login', [AuthController::class, 'login'])->name('login.post');
Route::post('/logout', [AuthController::class, 'logout'])->name('logout');

// تمام صفحات محافظت شده با middleware
Route::middleware(['web', App\Http\Middleware\Authenticate::class, App\Http\Middleware\RedirectIfSetupNeeded::class])->group(function () {

// صفحه اصلی - داشبورد
Route::get('/dashboard', [DashboardController::class, 'index'])->name('dashboard');

// مدیریت کاربران
Route::prefix('users')->group(function () {
    Route::get('/', [UserController::class, 'index'])->name('users.index');
    Route::get('/{userId}', [UserController::class, 'show'])->name('users.show');
    Route::post('/{userId}', [UserController::class, 'update'])->name('users.update');
    Route::delete('/{userId}', [UserController::class, 'destroy'])->name('users.destroy');
});

// مدیریت سرویس‌ها
Route::prefix('services')->group(function () {
    Route::get('/', [ServiceController::class, 'index'])->name('services.index');
    Route::get('/{id}', [ServiceController::class, 'show'])->name('services.show');
    Route::post('/{id}/toggle', [ServiceController::class, 'toggleStatus'])->name('services.toggle');
    Route::delete('/{id}', [ServiceController::class, 'destroy'])->name('services.destroy');
});

// مدیریت پلن‌ها
Route::prefix('plans')->group(function () {
    Route::get('/', [PlanController::class, 'index'])->name('plans.index');
    Route::get('/create', [PlanController::class, 'create'])->name('plans.create');
    Route::post('/', [PlanController::class, 'store'])->name('plans.store');
    Route::get('/{id}/edit', [PlanController::class, 'edit'])->name('plans.edit');
    Route::put('/{id}', [PlanController::class, 'update'])->name('plans.update');
    Route::delete('/{id}', [PlanController::class, 'destroy'])->name('plans.destroy');
});

// مدیریت پنل‌ها
Route::prefix('panels')->group(function () {
    Route::get('/', [PanelController::class, 'index'])->name('panels.index');
    Route::get('/create', [PanelController::class, 'create'])->name('panels.create');
    Route::post('/', [PanelController::class, 'store'])->name('panels.store');
    Route::get('/{id}/edit', [PanelController::class, 'edit'])->name('panels.edit');
    Route::put('/{id}', [PanelController::class, 'update'])->name('panels.update');
    Route::post('/{id}/toggle', [PanelController::class, 'toggleStatus'])->name('panels.toggle');
    Route::delete('/{id}', [PanelController::class, 'destroy'])->name('panels.destroy');
});

// مدیریت تراکنش‌ها
Route::prefix('transactions')->group(function () {
    Route::get('/', [TransactionController::class, 'index'])->name('transactions.index');
    Route::get('/{id}', [TransactionController::class, 'show'])->name('transactions.show');
    Route::post('/{id}/approve', [TransactionController::class, 'approve'])->name('transactions.approve');
    Route::post('/{id}/reject', [TransactionController::class, 'reject'])->name('transactions.reject');
});

// مدیریت بازاریاب‌ها
Route::prefix('marketers')->group(function () {
    Route::get('/', [MarketerController::class, 'index'])->name('marketers.index');
    Route::get('/{userId}', [MarketerController::class, 'show'])->name('marketers.show');
    Route::post('/{userId}/payout', [MarketerController::class, 'payout'])->name('marketers.payout');
});

// مدیریت کارت‌های هدیه
Route::prefix('gift-cards')->group(function () {
    Route::get('/', [GiftCardController::class, 'index'])->name('gift-cards.index');
    Route::get('/create', [GiftCardController::class, 'create'])->name('gift-cards.create');
    Route::post('/', [GiftCardController::class, 'store'])->name('gift-cards.store');
    Route::delete('/{id}', [GiftCardController::class, 'destroy'])->name('gift-cards.destroy');
});

// مدیریت کارت‌های بانکی
Route::prefix('card-accounts')->group(function () {
    Route::get('/', [CardAccountController::class, 'index'])->name('card-accounts.index');
    Route::get('/create', [CardAccountController::class, 'create'])->name('card-accounts.create');
    Route::post('/', [CardAccountController::class, 'store'])->name('card-accounts.store');
    Route::get('/{id}/edit', [CardAccountController::class, 'edit'])->name('card-accounts.edit');
    Route::put('/{id}', [CardAccountController::class, 'update'])->name('card-accounts.update');
    Route::post('/{id}/toggle', [CardAccountController::class, 'toggleStatus'])->name('card-accounts.toggle');
    Route::post('/{id}/reset', [CardAccountController::class, 'resetDailyAmount'])->name('card-accounts.reset');
    Route::delete('/{id}', [CardAccountController::class, 'destroy'])->name('card-accounts.destroy');
});

// تنظیمات
Route::prefix('settings')->group(function () {
    Route::get('/', [SettingController::class, 'index'])->name('settings.index');
    Route::post('/', [SettingController::class, 'update'])->name('settings.update');
    Route::get('/get/{key}', [SettingController::class, 'getSetting'])->name('settings.get');
    Route::post('/set/{key}', [SettingController::class, 'setSetting'])->name('settings.set');
});

// استارتر کیت (نمونه‌های قالب)
Route::prefix('starterkit')->group(function () {
    Route::view('layout-light', 'starterkit.layout-light')->name('layout-light');
    Route::view('layout-dark', 'starterkit.layout-dark')->name('layout-dark');
    Route::view('sidebar-fixed', 'starterkit.sidebar-fixed')->name('sidebar-fixed');
    Route::view('boxed', 'starterkit.boxed')->name('boxed');
    Route::view('layout-rtl', 'starterkit.layout-rtl')->name('layout-rtl');
    Route::view('vertical', 'starterkit.vertical')->name('vertical');
    Route::view('mega-menu', 'starterkit.mega-menu')->name('mega-menu');
});

// پاک‌سازی کش (فقط برای ادمین)
Route::get('/clear-cache', function() {
    if (!session()->has('user_authenticated') || session('user_role') !== 'admin') {
        abort(403);
    }
    Artisan::call('config:clear');
    Artisan::call('cache:clear');
    Artisan::call('view:clear');
    Artisan::call('route:clear');
    return redirect()->back()->with('success', 'کش با موفقیت پاک شد!');
})->name('clear.cache');

}); // پایان middleware group
