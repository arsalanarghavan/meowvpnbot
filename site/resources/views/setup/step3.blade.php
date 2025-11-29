@extends('layouts.app.master')
@section('title', 'مرحله 3 - تنظیمات پرداخت')

@section('content')
<div class="min-h-screen bg-gradient-to-br from-primary/20 to-primary/40 p-4">
    <div class="max-w-2xl mx-auto">
        <Card class="shadow-xl">
            <CardHeader>
                <div class="flex items-center justify-between">
                    <div>
                        <CardTitle class="text-2xl">مرحله 3: تنظیمات پرداخت و پشتیبانی</CardTitle>
                        <CardDescription>تنظیمات پرداخت و پشتیبانی را وارد کنید</CardDescription>
                    </div>
                    <Badge variant="outline">مرحله 3 از 4</Badge>
                </div>
                <div class="mt-4">
                    <div class="h-2 bg-muted rounded-full overflow-hidden">
                        <div class="h-full bg-primary rounded-full" style="width: 75%"></div>
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

                <Alert class="mb-4">
                    <AlertTitle>💡 نکته</AlertTitle>
                    <AlertDescription>
                        تمام این فیلدها اختیاری هستند و می‌توانید بعداً در تنظیمات تغییرشان دهید.
                    </AlertDescription>
                </Alert>

                <form method="POST" action="{{ route('setup.step3.save') }}" class="space-y-4">
                    @csrf

                    <div class="space-y-2">
                        <Label for="zarinpal_merchant">Merchant ID زرین‌پال (اختیاری)</Label>
                        <Input
                            id="zarinpal_merchant"
                            name="zarinpal_merchant"
                            type="text"
                            value="{{ old('zarinpal_merchant', session('setup_step3.zarinpal_merchant')) }}"
                            placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
                            :error="$errors->first('zarinpal_merchant')"
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="support_username">یوزرنیم پشتیبانی (اختیاری)</Label>
                        <Input
                            id="support_username"
                            name="support_username"
                            type="text"
                            value="{{ old('support_username', session('setup_step3.support_username')) }}"
                            placeholder="YourSupportID"
                            :error="$errors->first('support_username')"
                        />
                        <p class="text-xs text-muted-foreground">بدون @</p>
                    </div>

                    <div class="space-y-2">
                        <Label for="channel_id">آیدی کانال قفل عضویت (اختیاری)</Label>
                        <Input
                            id="channel_id"
                            name="channel_id"
                            type="text"
                            value="{{ old('channel_id', session('setup_step3.channel_id')) }}"
                            placeholder="@YourChannel"
                            :error="$errors->first('channel_id')"
                        />
                    </div>

                    <div class="flex gap-4">
                        <Button variant="outline" type="button" as="a" href="{{ route('setup.step2') }}" class="flex-1">قبلی</Button>
                        <Button type="submit" class="flex-1">ذخیره و ادامه</Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    </div>
</div>
@endsection

