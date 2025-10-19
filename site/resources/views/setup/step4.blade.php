<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>مرحله 4 - نصب</title>
    <link rel="stylesheet" href="{{asset('assets/css/bootstrap.css')}}">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 50px 0;
        }
        .wizard-container {
            max-width: 900px;
            margin: 0 auto;
        }
        .summary-box {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
        }
        .install-log {
            background: #1e1e1e;
            color: #00ff00;
            padding: 20px;
            border-radius: 8px;
            font-family: monospace;
            height: 300px;
            overflow-y: auto;
            display: none;
        }
        .btn-install {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            border-radius: 8px;
            padding: 15px 40px;
            font-weight: bold;
            color: white;
            font-size: 18px;
        }
        .spinner-border {
            display: none;
        }
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="card">
            <div class="card-header bg-success text-white text-center">
                <h4>مرحله 4 از 4 - بررسی و نصب</h4>
            </div>
            <div class="card-body">
                <h5 class="mb-4">خلاصه تنظیمات:</h5>

                <div class="summary-box">
                    <h6><strong>🤖 ربات تلگرام:</strong></h6>
                    <ul>
                        <li>یوزرنیم: @{{ $setup_data['step1']['bot_username'] }}</li>
                        <li>Telegram ID ادمین: {{ $setup_data['step1']['admin_telegram_id'] }}</li>
                    </ul>
                </div>

                <div class="summary-box">
                    <h6><strong>🌐 پنل :</strong></h6>
                    <ul>
                        <li>نام: {{ $setup_data['step2']['panel_name'] }}</li>
                        <li>نوع: {{ $setup_data['step2']['panel_type'] == 'marzban' ? 'Marzban' : 'Hiddify' }}</li>
                        <li>آدرس: {{ $setup_data['step2']['panel_url'] }}</li>
                    </ul>
                </div>

                <div class="summary-box">
                    <h6><strong>💳 تنظیمات اضافی:</strong></h6>
                    <ul>
                        <li>درگاه پرداخت: {{ !empty($setup_data['step3']['zarinpal_merchant']) ? 'فعال' : 'غیرفعال' }}</li>
                        <li>پشتیبانی: {{ !empty($setup_data['step3']['support_username']) ? '@'.$setup_data['step3']['support_username'] : 'تنظیم نشده' }}</li>
                        <li>کانال: {{ $setup_data['step3']['channel_id'] ?: 'تنظیم نشده' }}</li>
                    </ul>
                </div>

                <div class="alert alert-warning mt-4">
                    <strong>⚠️ توجه:</strong> با کلیک بر روی دکمه "شروع نصب"، فرآیند نصب خودکار ربات آغاز می‌شود. این ممکن است چند دقیقه طول بکشد.
                </div>

                <div id="installLog" class="install-log mt-4"></div>

                <div class="text-center mt-4">
                    <a href="{{ route('setup.step3') }}" class="btn btn-secondary" id="btnBack">قبلی →</a>
                    <button onclick="startInstallation()" class="btn btn-install" id="btnInstall">
                        <span class="spinner-border spinner-border-sm" id="spinner"></span>
                        <span id="btnText">🚀 شروع نصب</span>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script src="{{asset('assets/js/jquery-3.5.1.min.js')}}"></script>
    <script>
        function addLog(message) {
            var log = $('#installLog');
            log.show();
            log.append('[' + new Date().toLocaleTimeString() + '] ' + message + '\n');
            log.scrollTop(log[0].scrollHeight);
        }

        function startInstallation() {
            var btn = $('#btnInstall');
            var spinner = $('#spinner');
            var btnText = $('#btnText');
            var btnBack = $('#btnBack');

            // غیرفعال کردن دکمه‌ها
            btn.prop('disabled', true);
            btnBack.prop('disabled', true);
            spinner.show();
            btnText.text(' در حال نصب...');

            addLog('شروع فرآیند نصب...');
            addLog('ایجاد فایل تنظیمات ربات...');

            $.ajax({
                url: '{{ route("setup.install") }}',
                method: 'POST',
                data: {
                    _token: '{{ csrf_token() }}'
                },
                success: function(response) {
                    if (response.success) {
                        addLog('✓ فایل .env ایجاد شد');
                        addLog('✓ Dependencies نصب شد');
                        addLog('✓ Migrations اجرا شد');
                        addLog('✓ پنل  ثبت شد');
                        addLog('✓ ربات راه‌اندازی شد');
                        addLog('');
                        addLog('=== نصب با موفقیت انجام شد! ===');

                        setTimeout(function() {
                            window.location.href = response.redirect;
                        }, 2000);
                    } else {
                        addLog('✗ خطا: ' + response.message);
                        btn.prop('disabled', false);
                        btnBack.prop('disabled', false);
                        spinner.hide();
                        btnText.text('🚀 شروع نصب');
                    }
                },
                error: function(xhr) {
                    addLog('✗ خطای سرور: ' + (xhr.responseJSON?.message || 'خطای ناشناخته'));
                    btn.prop('disabled', false);
                    btnBack.prop('disabled', false);
                    spinner.hide();
                    btnText.text('🚀 شروع نصب');
                }
            });
        }
    </script>
</body>
</html>

