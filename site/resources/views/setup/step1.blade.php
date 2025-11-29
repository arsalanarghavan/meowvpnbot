@extends('layouts.app.master')
@section('title', 'مرحله 1 - تنظیمات ربات')

@section('content')
<div class="min-h-screen bg-gradient-to-br from-primary/20 to-primary/40 p-4">
    <div class="max-w-2xl mx-auto">
        <Card class="shadow-xl">
            <CardHeader>
                <div class="flex items-center justify-between">
                    <div>
                        <CardTitle class="text-2xl">مرحله 1: تنظیمات ربات تلگرام</CardTitle>
                        <CardDescription>اطلاعات ربات تلگرام را وارد کنید</CardDescription>
                    </div>
                    <Badge variant="outline">مرحله 1 از 4</Badge>
                </div>
                <div class="mt-4">
                    <div class="h-2 bg-muted rounded-full overflow-hidden">
                        <div class="h-full bg-primary rounded-full" style="width: 25%"></div>
                    </div>
                </div>
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

                <form method="POST" action="{{ route('setup.step1.save') }}" class="space-y-4">
                    @csrf

                    <div class="space-y-2">
                        <Label for="bot_token">توکن ربات</Label>
                        <Input
                            id="bot_token"
                            name="bot_token"
                            type="text"
                            value="{{ old('bot_token', session('setup_step1.bot_token')) }}"
                            placeholder="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
                            required
                            :error="$errors->first('bot_token')"
                        />
                        <p class="text-xs text-muted-foreground">
                            توکن ربات را از @BotFather دریافت کنید
                        </p>
                    </div>

                    <div class="space-y-2">
                        <Label for="bot_username">نام کاربری ربات</Label>
                        <Input
                            id="bot_username"
                            name="bot_username"
                            type="text"
                            value="{{ old('bot_username', session('setup_step1.bot_username')) }}"
                            placeholder="@mybot"
                            required
                            :error="$errors->first('bot_username')"
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="admin_telegram_id">شناسه تلگرام ادمین</Label>
                        <Input
                            id="admin_telegram_id"
                            name="admin_telegram_id"
                            type="number"
                            value="{{ old('admin_telegram_id', session('setup_step1.admin_telegram_id')) }}"
                            placeholder="123456789"
                            required
                            :error="$errors->first('admin_telegram_id')"
                        />
                        <p class="text-xs text-muted-foreground">
                            شناسه تلگرام خود را از @userinfobot دریافت کنید
                        </p>
                    </div>

                    <div class="flex gap-4">
                        <Button type="submit" class="flex-1">ذخیره و ادامه</Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    </div>
</div>
@endsection

