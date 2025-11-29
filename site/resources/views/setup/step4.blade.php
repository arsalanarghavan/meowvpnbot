@extends('layouts.app.master')
@section('title', 'مرحله 4 - نصب')

@section('content')
<div class="min-h-screen bg-gradient-to-br from-primary/20 to-primary/40 p-4">
    <div class="max-w-3xl mx-auto">
        <Card class="shadow-xl">
            <CardHeader>
                <div class="flex items-center justify-between">
                    <div>
                        <CardTitle class="text-2xl">مرحله 4: بررسی و نصب</CardTitle>
                        <CardDescription>بررسی تنظیمات و شروع نصب</CardDescription>
                    </div>
                    <Badge variant="outline">مرحله 4 از 4</Badge>
                </div>
                <div class="mt-4">
                    <div class="h-2 bg-muted rounded-full overflow-hidden">
                        <div class="h-full bg-primary rounded-full" style="width: 100%"></div>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div class="space-y-4">
                    <div>
                        <h3 class="font-semibold mb-2">🤖 ربات تلگرام:</h3>
                        <div class="bg-muted p-4 rounded-md space-y-1 text-sm">
                            <p><strong>یوزرنیم:</strong> @{{ $setup_data['step1']['bot_username'] }}</p>
                            <p><strong>Telegram ID ادمین:</strong> {{ $setup_data['step1']['admin_telegram_id'] }}</p>
                        </div>
                    </div>

                    <div>
                        <h3 class="font-semibold mb-2">🌐 پنل VPN:</h3>
                        <div class="bg-muted p-4 rounded-md space-y-1 text-sm">
                            <p><strong>نام:</strong> {{ $setup_data['step2']['panel_name'] }}</p>
                            <p><strong>نوع:</strong> {{ $setup_data['step2']['panel_type'] == 'marzban' ? 'Marzban' : 'Hiddify' }}</p>
                            <p><strong>آدرس:</strong> {{ $setup_data['step2']['panel_url'] }}</p>
                        </div>
                    </div>

                    <div>
                        <h3 class="font-semibold mb-2">💳 تنظیمات اضافی:</h3>
                        <div class="bg-muted p-4 rounded-md space-y-1 text-sm">
                            <p><strong>درگاه پرداخت:</strong> {{ !empty($setup_data['step3']['zarinpal_merchant']) ? 'فعال' : 'غیرفعال' }}</p>
                            <p><strong>پشتیبانی:</strong> {{ !empty($setup_data['step3']['support_username']) ? '@'.$setup_data['step3']['support_username'] : 'تنظیم نشده' }}</p>
                            <p><strong>کانال:</strong> {{ $setup_data['step3']['channel_id'] ?: 'تنظیم نشده' }}</p>
                        </div>
                    </div>

                    <Alert>
                        <AlertTitle>⚠️ توجه</AlertTitle>
                        <AlertDescription>
                            با کلیک بر روی دکمه "شروع نصب"، فرآیند نصب خودکار ربات آغاز می‌شود. این ممکن است چند دقیقه طول بکشد.
                        </AlertDescription>
                    </Alert>

                    <div id="installLog" class="hidden bg-black text-green-400 p-4 rounded-md font-mono text-sm h-64 overflow-y-auto">
                    </div>

                    <div class="flex gap-4">
                        <Button variant="outline" type="button" as="a" href="{{ route('setup.step3') }}" id="btnBack" class="flex-1">قبلی</Button>
                        <Button 
                            type="button" 
                            onclick="startInstallation()" 
                            id="btnInstall"
                            class="flex-1"
                            :loading="false"
                        >
                            <span id="btnText">🚀 شروع نصب</span>
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    </div>
</div>
@endsection

@section('scripts')
<script>
function addLog(message) {
    const log = document.getElementById('installLog');
    if (log) {
        log.classList.remove('hidden');
        const time = new Date().toLocaleTimeString('fa-IR');
        log.innerHTML += `[${time}] ${message}\n`;
        log.scrollTop = log.scrollHeight;
    }
}

function startInstallation() {
    const btn = document.getElementById('btnInstall');
    const btnText = document.getElementById('btnText');
    const btnBack = document.getElementById('btnBack');
    const log = document.getElementById('installLog');

    btn.disabled = true;
    btnBack.disabled = true;
    btnText.textContent = 'در حال نصب...';
    log.classList.remove('hidden');

    addLog('شروع فرآیند نصب...');
    addLog('ایجاد فایل تنظیمات ربات...');

    const installUrl = '{{ route("setup.install") }}';
    const csrfToken = document.querySelector('meta[name="csrf-token"]').content;

    fetch(installUrl, {
        method: 'POST',
        headers: {
            'X-CSRF-TOKEN': csrfToken,
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            _token: csrfToken
        })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.message || 'خطای سرور');
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            addLog('✓ فایل .env ایجاد شد');
            addLog('✓ Dependencies نصب شد');
            addLog('✓ Migrations اجرا شد');
            addLog('✓ پنل ثبت شد');
            addLog('✓ ربات راه‌اندازی شد');
            addLog('');
            addLog('=== نصب با موفقیت انجام شد! ===');

            setTimeout(() => {
                window.location.href = data.redirect || '/dashboard';
            }, 2000);
        } else {
            addLog('✗ خطا: ' + (data.message || 'خطای ناشناخته'));
            btn.disabled = false;
            btnBack.disabled = false;
            btnText.textContent = '🚀 شروع نصب';
        }
    })
    .catch(error => {
        addLog('✗ خطای سرور: ' + error.message);
        btn.disabled = false;
        btnBack.disabled = false;
        btnText.textContent = '🚀 شروع نصب';
    });
}
</script>
@endsection

