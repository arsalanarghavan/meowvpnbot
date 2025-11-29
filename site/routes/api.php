<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;
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

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
|
| Here is where you can register API routes for your application. These
| routes are loaded by the RouteServiceProvider within a group which
| is assigned the "api" middleware group. Enjoy building your API!
|
*/

// Protected API routes (require authentication)
Route::middleware(['web', App\Http\Middleware\Authenticate::class])->group(function () {
    
    // Dashboard Stats
    Route::get('/dashboard/stats', [DashboardController::class, 'stats'])->name('api.dashboard.stats');
    
    // Users API
    Route::prefix('users')->group(function () {
        Route::get('/', [UserController::class, 'apiIndex'])->name('api.users.index');
        Route::get('/{userId}', [UserController::class, 'apiShow'])->name('api.users.show');
        Route::put('/{userId}', [UserController::class, 'update'])->name('api.users.update');
        Route::delete('/{userId}', [UserController::class, 'destroy'])->name('api.users.destroy');
    });
    
    // Services API
    Route::prefix('services')->group(function () {
        Route::get('/', [ServiceController::class, 'apiIndex'])->name('api.services.index');
        Route::get('/{id}', [ServiceController::class, 'apiShow'])->name('api.services.show');
        Route::post('/{id}/toggle', [ServiceController::class, 'toggleStatus'])->name('api.services.toggle');
        Route::delete('/{id}', [ServiceController::class, 'destroy'])->name('api.services.destroy');
    });
    
    // Plans API
    Route::prefix('plans')->group(function () {
        Route::get('/', [PlanController::class, 'apiIndex'])->name('api.plans.index');
        Route::get('/{id}', [PlanController::class, 'apiShow'])->name('api.plans.show');
        Route::post('/', [PlanController::class, 'store'])->name('api.plans.store');
        Route::put('/{id}', [PlanController::class, 'update'])->name('api.plans.update');
        Route::delete('/{id}', [PlanController::class, 'destroy'])->name('api.plans.destroy');
    });
    
    // Panels API
    Route::prefix('panels')->group(function () {
        Route::get('/', [PanelController::class, 'apiIndex'])->name('api.panels.index');
        Route::get('/{id}', [PanelController::class, 'apiShow'])->name('api.panels.show');
        Route::post('/', [PanelController::class, 'store'])->name('api.panels.store');
        Route::put('/{id}', [PanelController::class, 'update'])->name('api.panels.update');
        Route::post('/{id}/toggle', [PanelController::class, 'toggleStatus'])->name('api.panels.toggle');
        Route::delete('/{id}', [PanelController::class, 'destroy'])->name('api.panels.destroy');
    });
    
    // Transactions API
    Route::prefix('transactions')->group(function () {
        Route::get('/', [TransactionController::class, 'apiIndex'])->name('api.transactions.index');
        Route::get('/{id}', [TransactionController::class, 'apiShow'])->name('api.transactions.show');
        Route::post('/{id}/approve', [TransactionController::class, 'approve'])->name('api.transactions.approve');
        Route::post('/{id}/reject', [TransactionController::class, 'reject'])->name('api.transactions.reject');
    });
    
    // Marketers API
    Route::prefix('marketers')->group(function () {
        Route::get('/', [MarketerController::class, 'apiIndex'])->name('api.marketers.index');
        Route::get('/{userId}', [MarketerController::class, 'apiShow'])->name('api.marketers.show');
        Route::post('/{userId}/payout', [MarketerController::class, 'payout'])->name('api.marketers.payout');
    });
    
    // Gift Cards API
    Route::prefix('gift-cards')->group(function () {
        Route::get('/', [GiftCardController::class, 'apiIndex'])->name('api.gift-cards.index');
        Route::get('/{id}', [GiftCardController::class, 'apiShow'])->name('api.gift-cards.show');
        Route::post('/', [GiftCardController::class, 'store'])->name('api.gift-cards.store');
        Route::delete('/{id}', [GiftCardController::class, 'destroy'])->name('api.gift-cards.destroy');
    });
    
    // Card Accounts API
    Route::prefix('card-accounts')->group(function () {
        Route::get('/', [CardAccountController::class, 'apiIndex'])->name('api.card-accounts.index');
        Route::get('/{id}', [CardAccountController::class, 'apiShow'])->name('api.card-accounts.show');
        Route::post('/', [CardAccountController::class, 'store'])->name('api.card-accounts.store');
        Route::put('/{id}', [CardAccountController::class, 'update'])->name('api.card-accounts.update');
        Route::post('/{id}/toggle', [CardAccountController::class, 'toggleStatus'])->name('api.card-accounts.toggle');
        Route::post('/{id}/reset', [CardAccountController::class, 'resetDailyAmount'])->name('api.card-accounts.reset');
        Route::delete('/{id}', [CardAccountController::class, 'destroy'])->name('api.card-accounts.destroy');
    });
    
    // Settings API
    Route::prefix('settings')->group(function () {
        Route::get('/', [SettingController::class, 'apiIndex'])->name('api.settings.index');
        Route::get('/{key}', [SettingController::class, 'getSetting'])->name('api.settings.get');
        Route::post('/{key}', [SettingController::class, 'setSetting'])->name('api.settings.set');
        Route::put('/', [SettingController::class, 'update'])->name('api.settings.update');
    });
    
});
