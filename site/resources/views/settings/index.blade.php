@extends('layouts.app.dashboard')
@section('title', 'تنظیمات')

@section('content')
<div class="space-y-6">
    <div>
        <h1 class="text-3xl font-bold tracking-tight">تنظیمات</h1>
        <p class="text-muted-foreground">تنظیمات کلی سیستم</p>
    </div>

    <Tabs default-value="general" class="w-full">
        <TabsList class="grid w-full grid-cols-4">
            <TabsTrigger value="general">عمومی</TabsTrigger>
            <TabsTrigger value="payment">پرداخت</TabsTrigger>
            <TabsTrigger value="bot">ربات</TabsTrigger>
            <TabsTrigger value="panel">پنل</TabsTrigger>
        </TabsList>

        <!-- تنظیمات عمومی -->
        <TabsContent value="general">
            <Card>
                <CardHeader>
                    <CardTitle>تنظیمات عمومی</CardTitle>
                    <CardDescription>تنظیمات کلی سیستم</CardDescription>
                </CardHeader>
                <CardContent>
                    <form method="POST" action="{{ route('settings.update') }}" class="space-y-4">
                        @csrf
                        <input type="hidden" name="section" value="general">
                        
                        <div class="space-y-2">
                            <Label for="support_username">نام کاربری پشتیبانی</Label>
                            <Input 
                                id="support_username" 
                                name="support_username" 
                                value="{{ $settings['support_username'] ?? '' }}"
                                placeholder="@username"
                            />
                        </div>

                        <div class="space-y-2">
                            <Label for="channel_id">شناسه کانال</Label>
                            <Input 
                                id="channel_id" 
                                name="channel_id" 
                                value="{{ $settings['channel_id'] ?? '' }}"
                                placeholder="-1001234567890"
                            />
                        </div>

                        <Button type="submit">ذخیره تغییرات</Button>
                    </form>
                </CardContent>
            </Card>
        </TabsContent>

        <!-- تنظیمات پرداخت -->
        <TabsContent value="payment">
            <Card>
                <CardHeader>
                    <CardTitle>تنظیمات پرداخت</CardTitle>
                    <CardDescription>تنظیمات درگاه پرداخت</CardDescription>
                </CardHeader>
                <CardContent>
                    <form method="POST" action="{{ route('settings.update') }}" class="space-y-4">
                        @csrf
                        <input type="hidden" name="section" value="payment">
                        
                        <div class="space-y-2">
                            <Label for="zarinpal_merchant">کد پذیرنده زرین‌پال</Label>
                            <Input 
                                id="zarinpal_merchant" 
                                name="zarinpal_merchant" 
                                value="{{ $settings['zarinpal_merchant'] ?? '' }}"
                            />
                        </div>

                        <Button type="submit">ذخیره تغییرات</Button>
                    </form>
                </CardContent>
            </Card>
        </TabsContent>

        <!-- تنظیمات ربات -->
        <TabsContent value="bot">
            <Card>
                <CardHeader>
                    <CardTitle>تنظیمات ربات</CardTitle>
                    <CardDescription>تنظیمات مربوط به ربات تلگرام</CardDescription>
                </CardHeader>
                <CardContent>
                    <form method="POST" action="{{ route('settings.update') }}" class="space-y-4">
                        @csrf
                        <input type="hidden" name="section" value="bot">
                        
                        <div class="space-y-2">
                            <Label for="bot_token">توکن ربات</Label>
                            <Input 
                                id="bot_token" 
                                name="bot_token" 
                                value="{{ $settings['bot_token'] ?? '' }}"
                                type="password"
                            />
                        </div>

                        <Button type="submit">ذخیره تغییرات</Button>
                    </form>
                </CardContent>
            </Card>
        </TabsContent>

        <!-- تنظیمات پنل -->
        <TabsContent value="panel">
            <Card>
                <CardHeader>
                    <CardTitle>تنظیمات پنل</CardTitle>
                    <CardDescription>تنظیمات مربوط به پنل VPN</CardDescription>
                </CardHeader>
                <CardContent>
                    <form method="POST" action="{{ route('settings.update') }}" class="space-y-4">
                        @csrf
                        <input type="hidden" name="section" value="panel">
                        
                        <div class="space-y-2">
                            <Label for="default_panel">پنل پیش‌فرض</Label>
                            <Select id="default_panel" name="default_panel">
                                <option value="">انتخاب کنید</option>
                                <!-- پنل‌ها از دیتابیس -->
                            </Select>
                        </div>

                        <Button type="submit">ذخیره تغییرات</Button>
                    </form>
                </CardContent>
            </Card>
        </TabsContent>
    </Tabs>
</div>
@endsection

