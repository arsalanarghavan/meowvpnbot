@extends('layouts.app.master')
@section('title', '500 - خطای سرور')

@section('content')
<div class="min-h-screen flex items-center justify-center p-4">
    <div class="text-center space-y-4 max-w-md">
        <h1 class="text-6xl font-bold">500</h1>
        <h2 class="text-2xl font-semibold">خطای سرور</h2>
        <p class="text-muted-foreground">متأسفانه خطایی در سرور رخ داده است. لطفاً بعداً تلاش کنید.</p>
        <div class="flex gap-4 justify-center">
            <Button as="a" href="{{ route('home') }}">بازگشت به صفحه اصلی</Button>
            <Button variant="outline" onclick="location.reload()">تلاش مجدد</Button>
        </div>
    </div>
</div>
@endsection

