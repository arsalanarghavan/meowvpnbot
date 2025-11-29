@extends('layouts.app.master')
@section('title', 'ورود به پنل مدیریت')

@section('content')
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/20 to-primary/40 p-4">
    <div class="w-full max-w-md">
        <Card class="shadow-xl">
            <CardHeader class="text-center">
                <CardTitle class="text-2xl">🐱 پنل مدیریت</CardTitle>
                <CardDescription>سیستم مدیریت ربات MeowVPN</CardDescription>
            </CardHeader>
            <CardContent>
                @if (session('success'))
                    <Alert variant="default" class="mb-4">
                        <AlertDescription>{{ session('success') }}</AlertDescription>
                    </Alert>
                @endif

                @if ($errors->any())
                    <Alert variant="destructive" class="mb-4">
                        <AlertTitle>خطا</AlertTitle>
                        <AlertDescription>
                            @foreach ($errors->all() as $error)
                                <div>{{ $error }}</div>
                            @endforeach
                        </AlertDescription>
                    </Alert>
                @endif

                <form method="POST" action="{{ route('login.post') }}" class="space-y-4">
                    @csrf

                    <div class="space-y-2">
                        <Label for="username">نام کاربری</Label>
                        <Input
                            id="username"
                            name="username"
                            type="text"
                            value="{{ old('username') }}"
                            required
                            autofocus
                            :error="$errors->first('username')"
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="password">رمز عبور</Label>
                        <Input
                            id="password"
                            name="password"
                            type="password"
                            required
                            :error="$errors->first('password')"
                        />
                    </div>

                    <Button type="submit" class="w-full" :loading="false">
                        ورود به پنل
                    </Button>
                </form>

                @if(env('SETUP_WIZARD_ENABLED', false) && !env('BOT_INSTALLED', false))
                <Alert class="mt-4">
                    <AlertTitle>⚠️ توجه</AlertTitle>
                    <AlertDescription>
                        سیستم هنوز راه‌اندازی نشده است.
                        بعد از ورود، لطفاً <a href="{{ route('setup') }}" class="underline">راه‌انداز</a> را تکمیل کنید.
                    </AlertDescription>
                </Alert>
                @endif
            </CardContent>
        </Card>
    </div>
</div>
@endsection

