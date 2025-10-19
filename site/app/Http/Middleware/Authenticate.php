<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class Authenticate
{
    /**
     * Handle an incoming request.
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @param  string|null  $role
     * @return mixed
     */
    public function handle(Request $request, Closure $next, $role = null)
    {
        // Check if user is logged in
        if (!session()->has('user_authenticated')) {
            return redirect()->route('login');
        }

        // Check role if specified
        if ($role && session('user_role') !== $role && session('user_role') !== 'admin') {
            abort(403, 'دسترسی غیرمجاز');
        }

        return $next($request);
    }
}
