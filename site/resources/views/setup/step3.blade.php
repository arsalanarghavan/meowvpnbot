<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مرحله 3 - تنظیمات پرداخت</title>
    <link rel="stylesheet" href="{{asset('assets/css/bootstrap.css')}}">
</head>
<body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 50px 0;">
    <div class="container" style="max-width: 800px;">
        <div class="card">
            <div class="card-header bg-primary text-white text-center">
                <h4>مرحله 3 از 4 - تنظیمات پرداخت و پشتیبانی</h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ route('setup.step3.save') }}">
                    @csrf
                    <div class="form-group">
                        <label>Merchant ID زرین‌پال (اختیاری)</label>
                        <input type="text" name="zarinpal_merchant" class="form-control" value="{{ old('zarinpal_merchant', session('setup_step3.zarinpal_merchant')) }}" placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx">
                        <small class="text-muted">اگر ندارید خالی بگذارید</small>
                    </div>
                    <div class="form-group">
                        <label>یوزرنیم پشتیبانی (اختیاری)</label>
                        <input type="text" name="support_username" class="form-control" value="{{ old('support_username', session('setup_step3.support_username')) }}" placeholder="YourSupportID">
                        <small class="text-muted">بدون @</small>
                    </div>
                    <div class="form-group">
                        <label>آیدی کانال قفل عضویت (اختیاری)</label>
                        <input type="text" name="channel_id" class="form-control" value="{{ old('channel_id', session('setup_step3.channel_id')) }}" placeholder="@YourChannel">
                    </div>
                    <div class="alert alert-info">
                        <strong>💡 نکته:</strong> تمام این فیلدها اختیاری هستند و می‌توانید بعداً در تنظیمات تغییرشان دهید.
                    </div>
                    <div class="text-center mt-4">
                        <a href="{{ route('setup.step2') }}" class="btn btn-secondary">قبلی →</a>
                        <button type="submit" class="btn btn-primary">بعدی ←</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>

