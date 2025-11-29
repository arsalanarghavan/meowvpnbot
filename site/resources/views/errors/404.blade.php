@extends('layouts.app.master')
@section('title', '404 - صفحه یافت نشد')

@section('content')
<div class="min-h-screen flex items-center justify-center p-4">
    <div class="text-center space-y-4">
        <h1 class="text-6xl font-bold">404</h1>
        <h2 class="text-2xl font-semibold">صفحه یافت نشد</h2>
        <p class="text-muted-foreground">صفحه‌ای که به دنبال آن هستید وجود ندارد.</p>
        <div class="flex gap-4 justify-center">
            <Button as="a" href="{{ route('home') }}">بازگشت به صفحه اصلی</Button>
            <Button variant="outline" onclick="history.back()">بازگشت</Button>
        </div>
    </div>
</div>
@endsection

