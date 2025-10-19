<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class EnsureSetupCompleted
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        // اگر Setup Wizard فعال نیست، ادامه بده
        if (!env('SETUP_WIZARD_ENABLED', false)) {
            return $next($request);
        }

        // اگر در مسیر setup هستیم، ادامه بده
        if ($request->is('setup*') || $request->is('backup*')) {
            return $next($request);
        }

        // اگر admin نساخته شده، به welcome برو
        if (empty(env('ADMIN_USERNAME'))) {
            return redirect()->route('setup.welcome');
        }

        // اگر bot نصب نشده، به setup برو
        if (!env('BOT_INSTALLED', false)) {
            // اگر لاگین نکرده، به login برو
            if (!session()->has('user_authenticated') && !$request->is('login')) {
                return redirect()->route('login');
            }

            // اگر لاگین کرده، به setup برو
            if (session()->has('user_authenticated')) {
                return redirect()->route('setup');
            }
        }

        return $next($request);
    }
}

