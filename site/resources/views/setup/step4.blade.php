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

            var installUrl = '{{ route("setup.install") }}';
            addLog('URL نصب: ' + installUrl);
            
            $.ajax({
                url: installUrl,
                method: 'POST',
                headers: {
                    'X-CSRF-TOKEN': $('meta[name="csrf-token"]').attr('content'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                data: {
                    _token: '{{ csrf_token() }}'
                },
                timeout: 300000, // 5 minutes timeout
                beforeSend: function() {
                    addLog('در حال ارسال درخواست به سرور...');
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
                error: function(xhr, status, error) {
                    var errorMessage = 'خطای ناشناخته';
                    
                    // بررسی نوع خطا
                    if (status === 'timeout') {
                        errorMessage = 'زمان درخواست به پایان رسید. این فرآیند ممکن است چند دقیقه طول بکشد.';
                    } else if (status === 'abort') {
                        errorMessage = 'درخواست لغو شد.';
                    } else if (xhr.status === 0) {
                        errorMessage = 'خطا در اتصال به سرور. لطفاً اتصال اینترنت و تنظیمات سرور را بررسی کنید.';
                    } else if (xhr.status === 419) {
                        errorMessage = 'خطای CSRF Token. لطفاً صفحه را refresh کنید و دوباره تلاش کنید.';
                    } else if (xhr.status === 500) {
                        errorMessage = 'خطای داخلی سرور. لطفاً لاگ‌های سرور را بررسی کنید.';
                    }
                    
                    // تلاش برای دریافت پیام خطا از response
                    if (xhr.responseJSON) {
                        if (xhr.responseJSON.message) {
                            errorMessage = xhr.responseJSON.message;
                        } else if (xhr.responseJSON.error) {
                            errorMessage = xhr.responseJSON.error;
                        }
                    } else if (xhr.responseText) {
                        try {
                            var parsed = JSON.parse(xhr.responseText);
                            if (parsed.message) {
                                errorMessage = parsed.message;
                            }
                        } catch(e) {
                            // اگر JSON نبود، از responseText استفاده کن
                            if (xhr.responseText.length < 200) {
                                errorMessage = xhr.responseText;
                            }
                        }
                    }
                    
                    addLog('✗ خطای سرور: ' + errorMessage);
                    addLog('✗ کد خطا: ' + xhr.status + ' | Status: ' + status);
                    addLog('✗ Error: ' + error);
                    
                    // نمایش alert برای خطاهای مهم
                    if (xhr.status === 500 || xhr.status === 0 || status === 'timeout') {
                        alert('خطا در نصب:\n\n' + errorMessage + '\n\nلطفاً لاگ‌های سرور را بررسی کنید:\ntail -f site/storage/logs/laravel.log');
                    }
                    
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

