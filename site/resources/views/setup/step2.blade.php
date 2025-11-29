@extends('layouts.app.master')
@section('title', 'مرحله 2 - پنل VPN')

@section('content')
<div class="min-h-screen bg-gradient-to-br from-primary/20 to-primary/40 p-4">
    <div class="max-w-2xl mx-auto">
        <Card class="shadow-xl">
            <CardHeader>
                <div class="flex items-center justify-between">
                    <div>
                        <CardTitle class="text-2xl">مرحله 2: پنل VPN</CardTitle>
                        <CardDescription>اطلاعات پنل VPN را وارد کنید</CardDescription>
                    </div>
                    <Badge variant="outline">مرحله 2 از 4</Badge>
                </div>
                <div class="mt-4">
                    <div class="h-2 bg-muted rounded-full overflow-hidden">
                        <div class="h-full bg-primary rounded-full" style="width: 50%"></div>
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

                <form method="POST" action="{{ route('setup.step2.save') }}" class="space-y-4">
                    @csrf

                    <div class="space-y-2">
                        <Label for="panel_name">نام پنل</Label>
                        <Input
                            id="panel_name"
                            name="panel_name"
                            type="text"
                            value="{{ old('panel_name', session('setup_step2.panel_name')) }}"
                            required
                            :error="$errors->first('panel_name')"
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="panel_type">نوع پنل</Label>
                        <Select id="panel_type" name="panel_type" required>
                            <option value="marzban" {{ old('panel_type', session('setup_step2.panel_type')) == 'marzban' ? 'selected' : '' }}>Marzban</option>
                            <option value="hiddify" {{ old('panel_type', session('setup_step2.panel_type')) == 'hiddify' ? 'selected' : '' }}>Hiddify</option>
                        </Select>
                    </div>

                    <div class="space-y-2">
                        <Label for="panel_url">آدرس URL پنل</Label>
                        <Input
                            id="panel_url"
                            name="panel_url"
                            type="url"
                            value="{{ old('panel_url', session('setup_step2.panel_url')) }}"
                            placeholder="https://panel.example.com"
                            required
                            :error="$errors->first('panel_url')"
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="panel_username">نام کاربری ادمین پنل</Label>
                        <Input
                            id="panel_username"
                            name="panel_username"
                            type="text"
                            value="{{ old('panel_username', session('setup_step2.panel_username')) }}"
                            required
                            :error="$errors->first('panel_username')"
                        />
                    </div>

                    <div class="space-y-2">
                        <Label for="panel_password">رمز عبور پنل</Label>
                        <Input
                            id="panel_password"
                            name="panel_password"
                            type="password"
                            required
                            :error="$errors->first('panel_password')"
                        />
                    </div>

                    <div class="flex gap-4">
                        <Button variant="outline" type="button" as="a" href="{{ route('setup.step1') }}" class="flex-1">قبلی</Button>
                        <Button type="submit" class="flex-1">ذخیره و ادامه</Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    </div>
</div>
@endsection

