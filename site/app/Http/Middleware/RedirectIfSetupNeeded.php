<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class RedirectIfSetupNeeded
{
    /**
     * Handle an incoming request.
     * اگر Setup Wizard فعال است و ربات نصب نشده، به /setup هدایت کن
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        // فقط برای صفحات احراز هویت شده
        if (session()->has('user_authenticated')) {
            // اگر Setup Wizard فعال است و ربات نصب نشده
            if (env('SETUP_WIZARD_ENABLED', false) && !env('BOT_INSTALLED', false)) {
                // اگر الان در مسیر setup نیست، redirect کن
                if (!$request->is('setup*')) {
                    return redirect()->route('setup')
                        ->with('warning', 'لطفاً ابتدا Setup Wizard را تکمیل کنید تا ربات نصب شود.');
                }
            }
        }

        return $next($request);
    }
}

