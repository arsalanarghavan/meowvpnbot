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
        // اگر در مسیر setup، backup یا login هستیم، همیشه ادامه بده (بدون هیچ redirect)
        if ($request->is('setup*') || $request->is('backup*') || $request->is('login*')) {
            return $next($request);
        }

        // اگر Setup Wizard فعال نیست، ادامه بده
        if (!env('SETUP_WIZARD_ENABLED', false)) {
            return $next($request);
        }

        // اگر admin نساخته نشده، به welcome برو
        if (empty(env('ADMIN_USERNAME'))) {
            return redirect()->route('setup.welcome');
        }

        // اگر bot نصب نشده
        if (!env('BOT_INSTALLED', false)) {
            // اگر لاگین نکرده، به welcome برو
            if (!session()->has('user_authenticated')) {
                return redirect()->route('setup.welcome');
            }
            // اگر لاگین کرده، به setup برو
            return redirect()->route('setup');
        }

        return $next($request);
    }
}

