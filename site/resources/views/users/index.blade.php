@extends('layouts.rtl.master')
@section('title', 'مدیریت کاربران')

@section('breadcrumb-title')
	<h2>مدیریت <span>کاربران</span></h2>
@endsection

@section('breadcrumb-items')
    <li class="breadcrumb-item">مدیریت</li>
	<li class="breadcrumb-item active">کاربران</li>
@endsection

@section('content')
<div class="container-fluid">
    <div class="row">
        <!-- آمار -->
        <div class="col-sm-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="media">
                        <div class="media-body">
                            <h6>کل کاربران</h6>
                            <h4 class="mb-0">{{ number_format($stats['total']) }}</h4>
                        </div>
                        <div class="bg-primary b-r-8"><i class="fa fa-users"></i></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="media">
                        <div class="media-body">
                            <h6>فعال</h6>
                            <h4 class="mb-0">{{ number_format($stats['active']) }}</h4>
                        </div>
                        <div class="bg-success b-r-8"><i class="fa fa-check"></i></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="media">
                        <div class="media-body">
                            <h6>بازاریاب‌ها</h6>
                            <h4 class="mb-0">{{ number_format($stats['marketers']) }}</h4>
                        </div>
                        <div class="bg-warning b-r-8"><i class="fa fa-bullhorn"></i></div>
                    </div>
                </div>
            </div>
        </div>
        <div class="col-sm-6 col-xl-3">
            <div class="card">
                <div class="card-body">
                    <div class="media">
                        <div class="media-body">
                            <h6>ادمین‌ها</h6>
                            <h4 class="mb-0">{{ number_format($stats['admins']) }}</h4>
                        </div>
                        <div class="bg-danger b-r-8"><i class="fa fa-shield"></i></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="row">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>لیست کاربران</h5>
                    <div class="card-header-right">
                        <form method="GET" class="form-inline">
                            <input type="text" name="search" class="form-control mr-2" placeholder="جستجو..." value="{{ request('search') }}">
                            <select name="role" class="form-control mr-2">
                                <option value="all">همه نقش‌ها</option>
                                <option value="customer" {{ request('role') == 'customer' ? 'selected' : '' }}>مشتری</option>
                                <option value="marketer" {{ request('role') == 'marketer' ? 'selected' : '' }}>بازاریاب</option>
                                <option value="admin" {{ request('role') == 'admin' ? 'selected' : '' }}>ادمین</option>
                            </select>
                            <select name="status" class="form-control mr-2">
                                <option value="all">همه وضعیت‌ها</option>
                                <option value="active" {{ request('status') == 'active' ? 'selected' : '' }}>فعال</option>
                                <option value="blocked" {{ request('status') == 'blocked' ? 'selected' : '' }}>مسدود</option>
                            </select>
                            <button type="submit" class="btn btn-primary">جستجو</button>
                        </form>
                    </div>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover">
                            <thead>
                                <tr>
                                    <th>شناسه کاربری</th>
                                    <th>نقش</th>
                                    <th>موجودی کیف پول</th>
                                    <th>موجودی کمیسیون</th>
                                    <th>تاریخ عضویت</th>
                                    <th>وضعیت</th>
                                    <th>عملیات</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($users as $user)
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
                                    <td>{{ number_format($user['commission_balance']) }} تومان</td>
                                    <td>{{ \Carbon\Carbon::parse($user['created_at'])->format('Y/m/d H:i') }}</td>
                                    <td>
                                        @if($user['is_active'])
                                            <span class="badge badge-success">فعال</span>
                                        @else
                                            <span class="badge badge-danger">مسدود</span>
                                        @endif
                                    </td>
                                    <td>
                                        <a href="{{ route('users.show', $user['user_id']) }}" class="btn btn-sm btn-primary">
                                            <i class="fa fa-eye"></i>
                                        </a>
                                    </td>
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

