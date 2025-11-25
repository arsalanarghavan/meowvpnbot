@extends('layouts.rtl.master')
@section('title', 'جزئیات کاربر')

@section('breadcrumb-title')
	<h2>جزئیات <span>کاربر</span></h2>
@endsection

@section('breadcrumb-items')
    <li class="breadcrumb-item"><a href="{{ route('users.index') }}">کاربران</a></li>
	<li class="breadcrumb-item active">{{ $user['user_id'] }}</li>
@endsection

@section('content')
<div class="container-fluid">
    <div class="row">
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>اطلاعات کاربر</h5>
                </div>
                <div class="card-body">
                    <table class="table table-borderless">
                        <tr>
                            <td><strong>شناسه:</strong></td>
                            <td>{{ $user['user_id'] }}</td>
                        </tr>
                        <tr>
                            <td><strong>نقش:</strong></td>
                            <td>
                                @if($user['role'] == 'admin')
                                    <span class="badge badge-danger">ادمین</span>
                                @elseif($user['role'] == 'marketer')
                                    <span class="badge badge-warning">بازاریاب</span>
                                @else
                                    <span class="badge badge-info">مشتری</span>
                                @endif
                            </td>
                        </tr>
                        <tr>
                            <td><strong>موجودی کیف پول:</strong></td>
                            <td>{{ number_format($user['wallet_balance']) }} تومان</td>
                        </tr>
                        <tr>
                            <td><strong>موجودی کمیسیون:</strong></td>
                            <td>{{ number_format($user['commission_balance']) }} تومان</td>
                        </tr>
                        <tr>
                            <td><strong>تاریخ عضویت:</strong></td>
                            <td>{{ \Carbon\Carbon::parse($user['created_at'])->format('Y/m/d H:i') }}</td>
                        </tr>
                        <tr>
                            <td><strong>وضعیت:</strong></td>
                            <td>
                                @if($user['is_active'])
                                    <span class="badge badge-success">فعال</span>
                                @else
                                    <span class="badge badge-danger">مسدود</span>
                                @endif
                            </td>
                        </tr>
                    </table>

                    <div class="mt-3">
                        <button class="btn btn-sm btn-primary btn-block" onclick="changeRole()">تغییر نقش</button>
                        <button class="btn btn-sm btn-info btn-block" onclick="addBalance()">افزایش موجودی</button>
                        <button class="btn btn-sm btn-warning btn-block" onclick="toggleStatus()">تغییر وضعیت</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5>سرویس‌های کاربر</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>نام کاربری</th>
                                <th>پلن</th>
                                <th>تاریخ انقضا</th>
                                <th>وضعیت</th>
                            </tr>
                        </thead>
                        <tbody>
                            @forelse($services as $service)
                            <tr>
                                <td>{{ $service['username_in_panel'] }}</td>
                                <td>{{ $service['plan_name'] }}</td>
                                <td>{{ \Carbon\Carbon::parse($service['expire_date'])->format('Y/m/d') }}</td>
                                <td>
                                    @if($service['is_active'])
                                        <span class="badge badge-success">فعال</span>
                                    @else
                                        <span class="badge badge-danger">منقضی</span>
                                    @endif
                                </td>
                            </tr>
                            @empty
                            <tr>
                                <td colspan="4" class="text-center">سرویسی یافت نشد</td>
                            </tr>
                            @endforelse
                        </tbody>
                    </table>
                </div>
            </div>

            <div class="card mt-3">
                <div class="card-header">
                    <h5>تراکنش‌های اخیر</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>مبلغ</th>
                                <th>نوع</th>
                                <th>وضعیت</th>
                                <th>تاریخ</th>
                            </tr>
                        </thead>
                        <tbody>
                            @forelse($transactions as $transaction)
                            <tr>
                                <td>{{ number_format($transaction['amount']) }} تومان</td>
                                <td>{{ $transaction['type'] }}</td>
                                <td>
                                    @if($transaction['status'] == 'موفق')
                                        <span class="badge badge-success">موفق</span>
                                    @elseif($transaction['status'] == 'در انتظار')
                                        <span class="badge badge-warning">در انتظار</span>
                                    @else
                                        <span class="badge badge-danger">ناموفق</span>
                                    @endif
                                </td>
                                <td>{{ \Carbon\Carbon::parse($transaction['created_at'])->format('Y/m/d H:i') }}</td>
                            </tr>
                            @empty
                            <tr>
                                <td colspan="4" class="text-center">تراکنشی یافت نشد</td>
                            </tr>
                            @endforelse
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@section('script')
<script src="{{asset('assets/js/sweet-alert/sweetalert.min.js')}}"></script>
<script>
const userId = {{ $user['user_id'] }};
const updateUrl = "{{ route('users.update', $user['user_id']) }}";

function changeRole() {
    swal({
        title: "تغییر نقش کاربر",
        text: "نقش جدید را انتخاب کنید:",
        type: "input",
        inputType: "select",
        inputOptions: {
            "customer": "مشتری",
            "marketer": "بازاریاب",
            "admin": "ادمین"
        },
        showCancelButton: true,
        confirmButtonText: "تغییر نقش",
        cancelButtonText: "لغو",
        inputPlaceholder: "نقش را انتخاب کنید",
        inputValidator: function(value) {
            return new Promise(function(resolve, reject) {
                if (value) {
                    resolve();
                } else {
                    reject("لطفاً یک نقش انتخاب کنید");
                }
            });
        }
    }).then(function(result) {
        if (result.value) {
            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    action: 'change_role',
                    role: result.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    swal("موفق!", "نقش کاربر با موفقیت تغییر کرد", "success")
                        .then(() => location.reload());
                } else {
                    swal("خطا!", data.message || "خطایی رخ داد", "error");
                }
            })
            .catch(error => {
                swal("خطا!", "خطا در ارتباط با سرور", "error");
            });
        }
    });
}

function addBalance() {
    swal({
        title: "افزایش موجودی",
        text: "مبلغ مورد نظر را وارد کنید (تومان):",
        type: "input",
        inputType: "number",
        showCancelButton: true,
        confirmButtonText: "افزایش موجودی",
        cancelButtonText: "لغو",
        inputPlaceholder: "مبلغ را وارد کنید",
        inputValidator: function(value) {
            return new Promise(function(resolve, reject) {
                if (value && parseFloat(value) > 0) {
                    resolve();
                } else {
                    reject("لطفاً یک مبلغ معتبر وارد کنید");
                }
            });
        }
    }).then(function(result) {
        if (result.value) {
            const amount = parseFloat(result.value);
            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    action: 'add_balance',
                    amount: amount
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    swal("موفق!", `موجودی کاربر ${amount.toLocaleString()} تومان افزایش یافت`, "success")
                        .then(() => location.reload());
                } else {
                    swal("خطا!", data.message || "خطایی رخ داد", "error");
                }
            })
            .catch(error => {
                swal("خطا!", "خطا در ارتباط با سرور", "error");
            });
        }
    });
}

function toggleStatus() {
    const currentStatus = {{ $user['is_active'] ? 'true' : 'false' }};
    const statusText = currentStatus ? "مسدود" : "فعال";
    
    swal({
        title: "تغییر وضعیت کاربر",
        text: `آیا مطمئن هستید که می‌خواهید کاربر را ${statusText} کنید؟`,
        type: "warning",
        showCancelButton: true,
        confirmButtonText: `بله، ${statusText} کن`,
        cancelButtonText: "لغو",
        confirmButtonColor: "#d33"
    }).then(function(result) {
        if (result.value) {
            fetch(updateUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': '{{ csrf_token() }}'
                },
                body: JSON.stringify({
                    action: 'toggle_status'
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    swal("موفق!", `وضعیت کاربر با موفقیت ${statusText} شد`, "success")
                        .then(() => location.reload());
                } else {
                    swal("خطا!", data.message || "خطایی رخ داد", "error");
                }
            })
            .catch(error => {
                swal("خطا!", "خطا در ارتباط با سرور", "error");
            });
        }
    });
}
</script>
@endsection

