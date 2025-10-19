<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ایجاد حساب ادمین - MeowVPN</title>
    <link rel="stylesheet" href="{{asset('assets/css/bootstrap.css')}}">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .setup-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 500px;
            width: 100%;
        }
        .setup-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 15px 15px 0 0;
        }
        .setup-body {
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
        .btn-create {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border: none;
            border-radius: 8px;
            padding: 15px;
            font-weight: bold;
            color: white;
            width: 100%;
        }
        .welcome-icon {
            font-size: 60px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="setup-card">
        <div class="setup-header">
            <div class="welcome-icon">🔐</div>
            <h3>ایجاد حساب ادمین</h3>
            <p>لطفاً اطلاعات ادمین اولیه را وارد کنید</p>
        </div>

        <div class="setup-body">
            <div class="alert alert-info">
                <strong>📌 مرحله اول:</strong> ایجاد حساب کاربری ادمین<br>
                <small>این اطلاعات برای ورود به پنل مدیریت استفاده می‌شود.</small>
            </div>

            @if ($errors->any())
                <div class="alert alert-danger">
                    @foreach ($errors->all() as $error)
                        <div>{{ $error }}</div>
                    @endforeach
                </div>
            @endif

            <form method="POST" action="{{ route('setup.welcome.save') }}" id="createAdminForm">
                @csrf

                <div class="form-group mb-3">
                    <label for="username"><strong>نام کاربری ادمین</strong> <span class="text-danger">*</span></label>
                    <input type="text"
                           class="form-control @error('username') is-invalid @enderror"
                           id="username"
                           name="username"
                           value="{{ old('username') }}"
                           placeholder="admin یا نام دلخواه شما"
                           required
                           autofocus
                           pattern="[a-zA-Z0-9_]{3,20}"
                           title="فقط حروف انگلیسی، اعداد و _ (حداقل 3 کاراکتر)">
                    <small class="text-muted">فقط حروف انگلیسی، اعداد و _ (حداقل 3 کاراکتر)</small>
                </div>

                <div class="form-group mb-3">
                    <label for="password"><strong>رمز عبور</strong> <span class="text-danger">*</span></label>
                    <input type="password"
                           class="form-control @error('password') is-invalid @enderror"
                           id="password"
                           name="password"
                           required
                           minlength="6"
                           placeholder="حداقل 6 کاراکتر">
                    <small class="text-muted">حداقل 6 کاراکتر، ترکیبی از حروف و اعداد توصیه می‌شود</small>
                </div>

                <div class="form-group mb-4">
                    <label for="password_confirmation"><strong>تکرار رمز عبور</strong> <span class="text-danger">*</span></label>
                    <input type="password"
                           class="form-control"
                           id="password_confirmation"
                           name="password_confirmation"
                           required
                           minlength="6"
                           placeholder="همان رمز عبور">
                </div>

                <div class="alert alert-warning">
                    <strong>⚠️ مهم:</strong> این اطلاعات را در جای امنی یادداشت کنید.<br>
                    بدون این اطلاعات نمی‌توانید وارد پنل شوید!
                </div>

                <button type="submit" class="btn btn-create mt-3">
                    ایجاد حساب و ادامه →
                </button>
            </form>
        </div>
    </div>

    <script src="{{asset('assets/js/jquery-3.5.1.min.js')}}"></script>
    <script>
        // بررسی تطابق رمزها
        document.getElementById('createAdminForm').addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmation = document.getElementById('password_confirmation').value;

            if (password !== confirmation) {
                e.preventDefault();
                alert('رمزهای عبور مطابقت ندارند!');
                return false;
            }

            if (password.length < 6) {
                e.preventDefault();
                alert('رمز عبور باید حداقل 6 کاراکتر باشد!');
                return false;
            }
        });
    </script>
</body>
</html>

