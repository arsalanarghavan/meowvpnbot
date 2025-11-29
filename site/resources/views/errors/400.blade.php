@extends('layouts.app.master')
@section('title', '400 - درخواست نامعتبر')

@section('content')
<div class="min-h-screen flex items-center justify-center p-4">
    <div class="text-center space-y-4 max-w-md">
        <h1 class="text-6xl font-bold">400</h1>
        <h2 class="text-2xl font-semibold">درخواست نامعتبر</h2>
        <p class="text-muted-foreground">درخواست شما نامعتبر است. لطفاً دوباره تلاش کنید.</p>
        <div class="flex gap-4 justify-center">
            <Button as="a" href="{{ route('home') }}">بازگشت به صفحه اصلی</Button>
            <Button variant="outline" onclick="history.back()">بازگشت</Button>
        </div>
    </div>
</div>
@endsection

