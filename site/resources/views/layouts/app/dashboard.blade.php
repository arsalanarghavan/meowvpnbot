<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'MeowVPN')</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @yield('styles')
</head>
<body class="min-h-screen bg-background">
    <div id="app">
        <AppLayout>
            @yield('content')
        </AppLayout>
    </div>
    @yield('scripts')
</body>
</html>

