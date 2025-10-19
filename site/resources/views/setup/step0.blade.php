<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>مرحله 0 - بازیابی دیتا</title>
    <link rel="stylesheet" href="{{asset('assets/css/bootstrap.css')}}">
    <link rel="stylesheet" href="{{asset('assets/css/style.css')}}">
    <style>
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 50px 0;
        }
        .wizard-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            max-width: 900px;
            margin: 0 auto;
        }
        .wizard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .wizard-body {
            padding: 40px;
        }
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .upload-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }
        .upload-area.dragover {
            background: #e8e9ff;
            border-color: #764ba2;
        }
        .file-info {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            display: none;
        }
        .btn-import {
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            border: none;
            border-radius: 8px;
            padding: 12px 30px;
            color: white;
            font-weight: bold;
        }
        .btn-skip {
            background: #6c757d;
            border: none;
            border-radius: 8px;
            padding: 12px 30px;
            color: white;
        }
    </style>
</head>
<body>
    <div class="wizard-card">
        <div class="wizard-header">
            <div class="step-indicator" style="color: white; font-weight: bold;">مرحله 0 از 4 (اختیاری)</div>
            <h3>📦 بازیابی دیتای قدیمی</h3>
            <p>اگر فایل بکاپ دارید، می‌توانید آن را import کنید</p>
        </div>

        <div class="wizard-body">
            <div class="alert alert-info">
                <strong>💡 این مرحله اختیاری است!</strong><br>
                اگر می‌خواهید از ابتدا شروع کنید، دکمه "رد کردن" را بزنید.
            </div>

            <div class="upload-area" id="uploadArea" onclick="document.getElementById('fileInput').click()">
                <i class="fa fa-cloud-upload" style="font-size: 50px; color: #667eea;"></i>
                <h5 class="mt-3">فایل بکاپ را اینجا بکشید یا کلیک کنید</h5>
                <p class="text-muted">فایل‌های پشتیبانی: .sql, .txt (حداکثر 50MB)</p>
                <input type="file" id="fileInput" accept=".sql,.txt" style="display: none;">
            </div>

            <div class="file-info mt-4" id="fileInfo">
                <h6><strong>اطلاعات فایل:</strong></h6>
                <table class="table table-sm">
                    <tr>
                        <td><strong>نام فایل:</strong></td>
                        <td id="fileName">-</td>
                    </tr>
                    <tr>
                        <td><strong>حجم:</strong></td>
                        <td id="fileSize">-</td>
                    </tr>
                    <tr>
                        <td><strong>نوع دیتابیس:</strong></td>
                        <td id="dbType">-</td>
                    </tr>
                    <tr>
                        <td><strong>تعداد جداول:</strong></td>
                        <td id="tableCount">-</td>
                    </tr>
                    <tr>
                        <td><strong>تعداد رکوردها:</strong></td>
                        <td id="recordCount">-</td>
                    </tr>
                </table>
            </div>

            <div id="importOptions" style="display: none;" class="mt-4">
                <h6><strong>چه چیزهایی Import شود؟</strong></h6>
                <div class="form-group">
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="import_type" id="importAll" value="all" checked>
                        <label class="form-check-label" for="importAll">
                            <strong>همه چیز</strong> - کاربران، تراکنش‌ها، سرویس‌ها
                        </label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="import_type" id="importUsers" value="users">
                        <label class="form-check-label" for="importUsers">
                            فقط کاربران و موجودی‌ها
                        </label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="import_type" id="importTrans" value="transactions">
                        <label class="form-check-label" for="importTrans">
                            فقط تراکنش‌ها
                        </label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="import_type" id="importServices" value="services">
                        <label class="form-check-label" for="importServices">
                            فقط سرویس‌ها
                        </label>
                    </div>
                </div>
            </div>

            <div class="alert alert-warning mt-4" id="warningBox" style="display: none;">
                <strong>⚠️ هشدار:</strong> این عملیات ممکن است چند دقیقه طول بکشد. لطفاً صبر کنید...
            </div>

            <div id="importProgress" style="display: none;" class="mt-4">
                <div class="progress">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width: 0%"></div>
                </div>
                <p class="text-center mt-2" id="progressText">در حال پردازش...</p>
            </div>

            <div class="text-center mt-5">
                <button class="btn btn-skip" onclick="skipImport()">
                    رد کردن →
                </button>
                <button class="btn btn-import" id="btnImport" onclick="startImport()" style="display: none;">
                    شروع Import
                </button>
            </div>
        </div>
    </div>

    <script src="{{asset('assets/js/jquery-3.5.1.min.js')}}"></script>
    <script>
        let selectedFile = null;

        // Handle file selection
        document.getElementById('fileInput').addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                selectedFile = e.target.files[0];
                analyzeFile(selectedFile);
            }
        });

        // Drag and drop
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');

            if (e.dataTransfer.files.length > 0) {
                selectedFile = e.dataTransfer.files[0];
                document.getElementById('fileInput').files = e.dataTransfer.files;
                analyzeFile(selectedFile);
            }
        });

        function analyzeFile(file) {
            const formData = new FormData();
            formData.append('backup_file', file);
            formData.append('_token', document.querySelector('meta[name="csrf-token"]').content);

            $.ajax({
                url: '/backup/analyze',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    if (response.success) {
                        // نمایش اطلاعات فایل
                        document.getElementById('fileName').textContent = file.name;
                        document.getElementById('fileSize').textContent = response.info.size;
                        document.getElementById('dbType').textContent = response.info.type;
                        document.getElementById('tableCount').textContent = response.info.tables;
                        document.getElementById('recordCount').textContent = response.info.inserts;

                        document.getElementById('fileInfo').style.display = 'block';
                        document.getElementById('importOptions').style.display = 'block';
                        document.getElementById('btnImport').style.display = 'inline-block';
                    }
                },
                error: function() {
                    alert('خطا در تحلیل فایل!');
                }
            });
        }

        function startImport() {
            if (!selectedFile) {
                alert('لطفاً ابتدا فایل را انتخاب کنید!');
                return;
            }

            const importType = document.querySelector('input[name="import_type"]:checked').value;

            document.getElementById('warningBox').style.display = 'block';
            document.getElementById('importProgress').style.display = 'block';
            document.getElementById('btnImport').disabled = true;

            const formData = new FormData();
            formData.append('backup_file', selectedFile);
            formData.append('import_type', importType);
            formData.append('_token', document.querySelector('meta[name="csrf-token"]').content);

            $.ajax({
                url: '/backup/import',
                method: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                xhr: function() {
                    const xhr = new window.XMLHttpRequest();
                    xhr.upload.addEventListener("progress", function(evt) {
                        if (evt.lengthComputable) {
                            const percentComplete = Math.round((evt.loaded / evt.total) * 100);
                            $('.progress-bar').css('width', percentComplete + '%');
                            document.getElementById('progressText').textContent = 'آپلود: ' + percentComplete + '%';
                        }
                    }, false);
                    return xhr;
                },
                success: function(response) {
                    if (response.success) {
                        $('.progress-bar').css('width', '100%');
                        document.getElementById('progressText').textContent = '✓ Import موفق!';

                        alert('دیتا با موفقیت import شد!\n\nکاربران: ' + (response.stats.users || 0));

                        // انتقال به مرحله بعد
                        window.location.href = '{{ route("setup.step1") }}';
                    } else {
                        alert('خطا: ' + response.message);
                        document.getElementById('btnImport').disabled = false;
                    }
                },
                error: function(xhr) {
                    alert('خطا در Import: ' + (xhr.responseJSON?.message || 'خطای ناشناخته'));
                    document.getElementById('btnImport').disabled = false;
                }
            });
        }

        function skipImport() {
            if (confirm('آیا مطمئن هستید که می‌خواهید این مرحله را رد کنید؟')) {
                window.location.href = '{{ route("setup.step1") }}';
            }
        }
    </script>
</body>
</html>

