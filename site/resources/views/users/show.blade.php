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
function changeRole() {
    // TODO: پیاده‌سازی تغییر نقش
    alert('در حال توسعه');
}

function addBalance() {
    // TODO: پیاده‌سازی افزایش موجودی
    alert('در حال توسعه');
}

function toggleStatus() {
    if (confirm('آیا مطمئن هستید؟')) {
        // TODO: پیاده‌سازی تغییر وضعیت
        alert('در حال توسعه');
    }
}
</script>
@endsection

