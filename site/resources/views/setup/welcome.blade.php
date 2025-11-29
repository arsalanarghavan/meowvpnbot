@extends('layouts.app.master')
@section('title', 'ایجاد حساب ادمین')

@section('content')
<div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary/20 to-primary/40 p-4">
    <div class="w-full max-w-md">
        <Card class="shadow-xl">
            <CardHeader class="text-center">
                <CardTitle class="text-2xl">🐱 خوش آمدید</CardTitle>
                <CardDescription>برای شروع، حساب ادمین ایجاد کنید</CardDescription>
            </CardHeader>
            <CardContent>
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

                <form method="POST" action="{{ route('setup.welcome.save') }}" class="space-y-4">
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

                    <div class="space-y-2">
                        <Label for="password_confirmation">تکرار رمز عبور</Label>
                        <Input
                            id="password_confirmation"
                            name="password_confirmation"
                            type="password"
                            required
                            :error="$errors->first('password_confirmation')"
                        />
                    </div>

                    <Button type="submit" class="w-full">ایجاد حساب و ادامه</Button>
                </form>
            </CardContent>
        </Card>
    </div>
</div>
@endsection

