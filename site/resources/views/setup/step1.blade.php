<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مرحله 1 - تنظیمات ربات تلگرام</title>
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
        }
        .wizard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .progress-bar-custom {
            height: 5px;
            background: #e0e0e0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            width: 25%;
            transition: width 0.3s;
        }
        .wizard-body {
            padding: 40px;
        }
        .form-control {
            border-radius: 8px;
            padding: 12px;
            border: 2px solid #e0e0e0;
        }
        .form-control:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
        }
        .btn-next {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            padding: 12px 30px;
            font-weight: bold;
            color: white;
        }
        .help-text {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            font-size: 14px;
        }
        .step-indicator {
            text-align: center;
            margin: 20px 0;
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="wizard-container">
        <div class="wizard-card">
            <div class="progress-bar-custom">
                <div class="progress-fill"></div>
            </div>

            <div class="wizard-header">
                <div class="step-indicator">مرحله 1 از 4</div>
                <h3>🤖 تنظیمات ربات تلگرام</h3>
                <p>اطلاعات ربات خود را وارد کنید</p>
            </div>

            <div class="wizard-body">
                @if ($errors->any())
                    <div class="alert alert-danger">
                        @foreach ($errors->all() as $error)
                            <div>{{ $error }}</div>
                        @endforeach
                    </div>
                @endif

                <form method="POST" action="{{ route('setup.step1.save') }}">
                    @csrf

                    <div class="form-group mb-4">
                        <label for="bot_token"><strong>توکن ربات تلگرام</strong> <span class="text-danger">*</span></label>
                        <input type="text"
                               class="form-control @error('bot_token') is-invalid @enderror"
                               id="bot_token"
                               name="bot_token"
                               value="{{ old('bot_token', session('setup_step1.bot_token')) }}"
                               placeholder="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"
                               required>
                        <small class="text-muted">توکن را از @BotFather دریافت کنید</small>
                    </div>

                    <div class="form-group mb-4">
                        <label for="bot_username"><strong>یوزرنیم ربات</strong> <span class="text-danger">*</span></label>
                        <input type="text"
                               class="form-control @error('bot_username') is-invalid @enderror"
                               id="bot_username"
                               name="bot_username"
                               value="{{ old('bot_username', session('setup_step1.bot_username')) }}"
                               placeholder="YourBotUsername"
                               required>
                        <small class="text-muted">بدون @ (مثال: MyVPNBot)</small>
                    </div>

                    <div class="form-group mb-4">
                        <label for="admin_telegram_id"><strong>Telegram ID ادمین</strong> <span class="text-danger">*</span></label>
                        <input type="number"
                               class="form-control @error('admin_telegram_id') is-invalid @enderror"
                               id="admin_telegram_id"
                               name="admin_telegram_id"
                               value="{{ old('admin_telegram_id', session('setup_step1.admin_telegram_id')) }}"
                               placeholder="123456789"
                               required>
                        <small class="text-muted">ID تلگرام خود را از @userinfobot دریافت کنید</small>
                    </div>

                    <div class="help-text">
                        <strong>📝 راهنما:</strong>
                        <ol class="mb-0 mt-2">
                            <li>به @BotFather در تلگرام بروید</li>
                            <li>دستور /newbot را ارسال کنید</li>
                            <li>نام و یوزرنیم ربات را تعیین کنید</li>
                            <li>توکن دریافتی را در بالا وارد کنید</li>
                            <li>برای دریافت ID خود به @userinfobot بروید</li>
                        </ol>
                    </div>

                    <div class="text-center mt-5">
                        <button type="submit" class="btn btn-next">
                            مرحله بعد ←
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>

