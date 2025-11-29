<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\Str;

class ThrottleLogin
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next, $maxAttempts = 5, $decayMinutes = 15)
    {
        $key = $this->resolveRequestSignature($request);

        if (RateLimiter::tooManyAttempts($key, $maxAttempts)) {
            $seconds = RateLimiter::availableIn($key);
            
            return back()->withErrors([
                'username' => "تعداد تلاش‌های ناموفق بیش از حد مجاز است. لطفاً {$seconds} ثانیه دیگر تلاش کنید.",
            ])->withInput($request->only('username'));
        }

        RateLimiter::hit($key, $decayMinutes * 60);

        $response = $next($request);

        // اگر لاگین موفق بود، rate limit را پاک کن
        if ($response->getStatusCode() === 302 && session()->has('user_authenticated')) {
            RateLimiter::clear($key);
        }

        return $response;
    }

    /**
     * Resolve request signature.
     *
     * @param  \Illuminate\Http\Request  $request
     * @return string
     */
    protected function resolveRequestSignature($request)
    {
        return Str::lower($request->input('username') . '|' . $request->ip());
    }
}

