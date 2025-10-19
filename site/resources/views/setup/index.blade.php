<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Setup Wizard - MeowVPN</title>
    <link rel="stylesheet" href="{{asset('assets/css/bootstrap.css')}}">
    <link rel="stylesheet" href="{{asset('assets/css/style.css')}}">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 50px 0;
        }
        .wizard-container {
            max-width: 800px;
            margin: 0 auto;
        }
        .wizard-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .wizard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .wizard-header h2 {
            margin: 0;
            font-weight: bold;
        }
        .wizard-body {
            padding: 40px;
        }
        .welcome-icon {
            font-size: 80px;
            margin: 20px 0;
        }
        .feature-list {
            text-align: right;
            margin: 30px 0;
        }
        .feature-list li {
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        .btn-start {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            padding: 15px 40px;
            font-weight: bold;
            color: white;
            font-size: 18px;
        }
        .btn-start:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="wizard-card">
            <div class="wizard-header">
                <div class="welcome-icon">🐱</div>
                <h2>خوش آمدید به Setup Wizard</h2>
                <p>راه‌اندازی MeowVPN Bot در 4 مرحله ساده</p>
            </div>

            <div class="wizard-body text-center">
                <div class="alert alert-success">
                    <strong>✅ پنل وب با موفقیت نصب شد!</strong><br>
                    <small>حالا باید ربات تلگرام را نصب و راه‌اندازی کنید.</small>
                </div>

                <h4 class="mt-4">این ویزارد در 4 مرحله ساده:</h4>

                <ul class="feature-list list-unstyled">
                    <li>✅ تنظیم ربات تلگرام</li>
                    <li>✅ اتصال به پنل VPN (Marzban/Hiddify)</li>
                    <li>✅ تنظیم درگاه پرداخت (اختیاری)</li>
                    <li>✅ راه‌اندازی خودکار ربات</li>
                </ul>

                <div class="alert alert-warning mt-4">
                    <strong>💡 نکته:</strong> اطلاعات به صورت امن ذخیره می‌شود.<br>
                    فرآیند کامل فقط 5 دقیقه زمان می‌برد.
                </div>

                <div class="alert alert-info mt-3">
                    <strong>📝 آماده باشید:</strong>
                    <ul class="text-right mb-0">
                        <li>توکن ربات از @BotFather</li>
                        <li>اطلاعات پنل VPN (Marzban/Hiddify)</li>
                        <li>Merchant ID زرین‌پال (اختیاری)</li>
                    </ul>
                </div>

                <div class="mt-5">
                    <a href="{{ route('setup.step1') }}" class="btn btn-start">
                        🚀 نصب جدید (از ابتدا)
                    </a>
                </div>

                <div class="mt-3">
                    <a href="{{ route('setup.step0') }}" class="btn" style="background: #6c757d; color: white; border-radius: 8px; padding: 12px 30px;">
                        📦 بازیابی از بکاپ قدیمی
                    </a>
                </div>

                <div class="mt-4">
                    <small class="text-muted">
                        • اگر فایل بکاپ (demo.sql) دارید، از گزینه "بازیابی" استفاده کنید<br>
                        • این ویزارد فقط یک بار قابل اجراست و بعد از نصب غیرفعال می‌شود
                    </small>
                </div>
            </div>
        </div>
    </div>
</body>
</html>

