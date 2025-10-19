@extends('layouts.rtl.master')
@section('title', 'داشبورد')

@section('css')
<link rel="stylesheet" type="text/css" href="{{asset('assets/css/chartist.css')}}">
<link rel="stylesheet" type="text/css" href="{{asset('assets/css/date-picker.css')}}">
@endsection

@section('style')
@endsection

@section('breadcrumb-title')
	<h2>داشبورد <span>مدیریت </span></h2>
@endsection

@section('breadcrumb-items')
    <li class="breadcrumb-item active">داشبورد</li>
@endsection

@section('content')
<div class="container-fluid">
    <div class="row">
        <!-- آمار کاربران -->
        <div class="col-xl-3 col-sm-6">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">کل کاربران</h6>
                            <h4 class="mb-0">{{ number_format($stats['users']['total']) }}</h4>
                        </div>
                        <div class="flex-shrink-0">
                            <div class="avatar-sm rounded-circle bg-primary align-self-center mini-stat-icon">
                                <span class="avatar-title rounded-circle bg-primary">
                                    <i class="fa fa-users font-primary"></i>
                                </span>
                            </div>
                        </div>
                    </div>
                    <p class="text-muted mt-3 mb-0">
                        <span class="badge badge-success mr-1">{{ number_format($stats['users']['active']) }}</span>
                        <span class="text-muted">فعال</span>
                        <span class="badge badge-danger mr-1 ml-2">{{ number_format($stats['users']['blocked']) }}</span>
                        <span class="text-muted">مسدود</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- آمار سرویس‌ها -->
        <div class="col-xl-3 col-sm-6">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">کل سرویس‌ها</h6>
                            <h4 class="mb-0">{{ number_format($stats['services']['total']) }}</h4>
                        </div>
                        <div class="flex-shrink-0">
                            <div class="avatar-sm rounded-circle bg-success align-self-center mini-stat-icon">
                                <span class="avatar-title rounded-circle bg-success">
                                    <i class="fa fa-server font-success"></i>
                                </span>
                            </div>
                        </div>
                    </div>
                    <p class="text-muted mt-3 mb-0">
                        <span class="badge badge-success mr-1">{{ number_format($stats['services']['active']) }}</span>
                        <span class="text-muted">فعال</span>
                        <span class="badge badge-warning mr-1 ml-2">{{ number_format($stats['services']['expiring']) }}</span>
                        <span class="text-muted">در حال انقضا</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- آمار درآمد -->
        <div class="col-xl-3 col-sm-6">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">درآمد کل</h6>
                            <h4 class="mb-0">{{ number_format($stats['revenue']['total']) }} تومان</h4>
                        </div>
                        <div class="flex-shrink-0">
                            <div class="avatar-sm rounded-circle bg-info align-self-center mini-stat-icon">
                                <span class="avatar-title rounded-circle bg-info">
                                    <i class="fa fa-money font-info"></i>
                                </span>
                            </div>
                        </div>
                    </div>
                    <p class="text-muted mt-3 mb-0">
                        <span class="text-muted">۳۰ روز اخیر:</span>
                        <span class="badge badge-info mr-1">{{ number_format($stats['revenue']['monthly']) }}</span>
                        <span class="text-muted">تومان</span>
                    </p>
                </div>
            </div>
        </div>

        <!-- آمار بازاریاب‌ها -->
        <div class="col-xl-3 col-sm-6">
            <div class="card">
                <div class="card-body">
                    <div class="d-flex">
                        <div class="flex-grow-1">
                            <h6 class="mb-2">بازاریاب‌ها</h6>
                            <h4 class="mb-0">{{ number_format($stats['users']['marketers']) }}</h4>
                        </div>
                        <div class="flex-shrink-0">
                            <div class="avatar-sm rounded-circle bg-warning align-self-center mini-stat-icon">
                                <span class="avatar-title rounded-circle bg-warning">
                                    <i class="fa fa-bullhorn font-warning"></i>
                                </span>
                            </div>
                        </div>
                    </div>
                    <p class="text-muted mt-3 mb-0">
                        <span class="text-muted">کمیسیون پرداخت نشده:</span>
                        <span class="badge badge-warning mr-1">{{ number_format($stats['commissions']['unpaid']) }}</span>
                    </p>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <!-- آمار اضافی -->
        <div class="col-xl-4 col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>آمار پلن‌ها و پنل‌ها</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            کل پلن‌ها
                            <span class="badge badge-primary badge-pill">{{ number_format($stats['plans']['total']) }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            کل پنل‌ها
                            <span class="badge badge-success badge-pill">{{ number_format($stats['panels']['total']) }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            پنل‌های فعال
                            <span class="badge badge-success badge-pill">{{ number_format($stats['panels']['active']) }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            تراکنش‌های در انتظار
                            <span class="badge badge-warning badge-pill">{{ number_format($stats['revenue']['pending']) }}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- آمار کارت‌های هدیه -->
        <div class="col-xl-4 col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>کارت‌های هدیه</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            کل کارت‌ها
                            <span class="badge badge-primary badge-pill">{{ number_format($stats['giftCards']['total']) }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            استفاده شده
                            <span class="badge badge-success badge-pill">{{ number_format($stats['giftCards']['used']) }}</span>
                        </li>
                        <li class="list-group-item d-flex justify-content-between align-items-center">
                            استفاده نشده
                            <span class="badge badge-info badge-pill">{{ number_format($stats['giftCards']['unused']) }}</span>
                        </li>
                    </ul>
                </div>
            </div>
        </div>

        <!-- نمودار درآمد -->
        <div class="col-xl-4 col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>درآمد ۳۰ روز اخیر</h5>
                </div>
                <div class="card-body">
                    <canvas id="revenueChart" height="200"></canvas>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <!-- آخرین کاربران -->
        <div class="col-xl-6">
            <div class="card">
                <div class="card-header">
                    <h5>آخرین کاربران</h5>
                    <a href="{{ route('users.index') }}" class="btn btn-sm btn-primary">مشاهده همه</a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>شناسه</th>
                                    <th>نقش</th>
                                    <th>موجودی</th>
                                    <th>تاریخ عضویت</th>
                                    <th>وضعیت</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($stats['latestUsers'] as $user)
                                <tr>
                                    <td><a href="{{ route('users.show', $user['user_id']) }}">{{ $user['user_id'] }}</a></td>
                                    <td>
                                        @if($user['role'] == 'customer')
                                            <span class="badge badge-info">مشتری</span>
                                        @elseif($user['role'] == 'marketer')
                                            <span class="badge badge-warning">بازاریاب</span>
                                        @else
                                            <span class="badge badge-danger">ادمین</span>
                                        @endif
                                    </td>
                                    <td>{{ number_format($user['wallet_balance']) }} تومان</td>
                                    <td>{{ \Carbon\Carbon::parse($user['created_at'])->format('Y/m/d') }}</td>
                                    <td>
                                        @if($user['is_active'])
                                            <span class="badge badge-success">فعال</span>
                                        @else
                                            <span class="badge badge-danger">مسدود</span>
                                        @endif
                                    </td>
                                </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- آخرین تراکنش‌ها -->
        <div class="col-xl-6">
            <div class="card">
                <div class="card-header">
                    <h5>آخرین تراکنش‌ها</h5>
                    <a href="{{ route('transactions.index') }}" class="btn btn-sm btn-primary">مشاهده همه</a>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>کاربر</th>
                                    <th>مبلغ</th>
                                    <th>نوع</th>
                                    <th>وضعیت</th>
                                    <th>تاریخ</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($stats['latestTransactions'] as $transaction)
                                <tr>
                                    <td><a href="{{ route('users.show', $transaction['user_id']) }}">{{ $transaction['user_id'] }}</a></td>
                                    <td>{{ number_format($transaction['amount']) }} تومان</td>
                                    <td><span class="badge badge-info">{{ $transaction['type'] }}</span></td>
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
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
@endsection

@section('script')
<script src="{{asset('assets/js/chart/chartjs/chart.min.js')}}"></script>
<script>
    // نمودار درآمد
    var ctx = document.getElementById('revenueChart').getContext('2d');
    var revenueData = @json($stats['revenueChart']);
    
    var labels = revenueData.map(function(item) {
        return item.date;
    });
    
    var data = revenueData.map(function(item) {
        return item.total;
    });
    
    var myChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'درآمد (تومان)',
                data: data,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
</script>
@endsection
