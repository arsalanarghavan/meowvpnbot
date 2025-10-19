<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>مرحله 2 - پنل </title>
    <link rel="stylesheet" href="{{asset('assets/css/bootstrap.css')}}">
    <link rel="stylesheet" href="{{asset('assets/css/style.css')}}">
</head>
<body style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 50px 0;">
    <div class="container" style="max-width: 800px;">
        <div class="card">
            <div class="card-header bg-primary text-white text-center">
                <h4>مرحله 2 از 4 - پنل </h4>
            </div>
            <div class="card-body">
                <form method="POST" action="{{ route('setup.step2.save') }}">
                    @csrf
                    <div class="form-group">
                        <label>نام پنل</label>
                        <input type="text" name="panel_name" class="form-control" value="{{ old('panel_name', session('setup_step2.panel_name')) }}" required>
                    </div>
                    <div class="form-group">
                        <label>نوع پنل</label>
                        <select name="panel_type" class="form-control" required>
                            <option value="marzban">Marzban</option>
                            <option value="hiddify">Hiddify</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>آدرس URL پنل</label>
                        <input type="url" name="panel_url" class="form-control" value="{{ old('panel_url', session('setup_step2.panel_url')) }}" placeholder="https://panel.example.com" required>
                    </div>
                    <div class="form-group">
                        <label>نام کاربری ادمین پنل</label>
                        <input type="text" name="panel_username" class="form-control" value="{{ old('panel_username', session('setup_step2.panel_username')) }}" required>
                    </div>
                    <div class="form-group">
                        <label>رمز عبور پنل</label>
                        <input type="password" name="panel_password" class="form-control" required>
                    </div>
                    <div class="text-center mt-4">
                        <a href="{{ route('setup.step1') }}" class="btn btn-secondary">→ قبلی</a>
                        <button type="submit" class="btn btn-primary">بعدی ←</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</body>
</html>

