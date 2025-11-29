@extends('layouts.app.dashboard')
@section('title', 'داشبورد')

@section('content')
<div class="space-y-6">
    <div>
        <h1 class="text-3xl font-bold tracking-tight">داشبورد</h1>
        <p class="text-muted-foreground">خلاصه آمار و اطلاعات سیستم</p>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <!-- آمار کاربران -->
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">کل کاربران</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['users']['total']) }}</div>
                <p class="text-xs text-muted-foreground mt-1">
                    <Badge variant="secondary" class="mr-1">{{ number_format($stats['users']['active']) }} فعال</Badge>
                    <Badge variant="destructive">{{ number_format($stats['users']['blocked']) }} مسدود</Badge>
                </p>
            </CardContent>
        </Card>

        <!-- آمار سرویس‌ها -->
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">کل سرویس‌ها</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <rect width="20" height="14" x="2" y="5" rx="2"></rect>
                    <path d="M2 10h20"></path>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['services']['total']) }}</div>
                <p class="text-xs text-muted-foreground mt-1">
                    <Badge variant="secondary" class="mr-1">{{ number_format($stats['services']['active']) }} فعال</Badge>
                    <Badge variant="outline">{{ number_format($stats['services']['expiring']) }} در حال انقضا</Badge>
                </p>
            </CardContent>
        </Card>

        <!-- آمار درآمد -->
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">درآمد کل</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['revenue']['total']) }} تومان</div>
                <p class="text-xs text-muted-foreground mt-1">
                    ۳۰ روز اخیر: {{ number_format($stats['revenue']['monthly']) }} تومان
                </p>
            </CardContent>
        </Card>

        <!-- آمار تراکنش‌ها -->
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">تراکنش‌های امروز</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['transactions']['today']) }}</div>
                <p class="text-xs text-muted-foreground mt-1">
                    <Badge variant="outline" class="mr-1">{{ number_format($stats['revenue']['pending']) }} در انتظار</Badge>
                </p>
            </CardContent>
        </Card>
    </div>

    <!-- جداول و اطلاعات بیشتر -->
    <div class="grid gap-4 md:grid-cols-2">
        <Card>
            <CardHeader>
                <CardTitle>آخرین کاربران</CardTitle>
                <CardDescription>کاربران جدید ثبت‌نام شده</CardDescription>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>نام کاربری</TableHead>
                            <TableHead>نقش</TableHead>
                            <TableHead>تاریخ ثبت</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($stats['latestUsers'] ?? [] as $user)
                        <TableRow>
                            <TableCell>{{ $user['user_id'] }}</TableCell>
                            <TableCell>
                                <Badge>{{ $user['role'] }}</Badge>
                            </TableCell>
                            <TableCell>{{ \Carbon\Carbon::parse($user['created_at'])->format('Y/m/d') }}</TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="3" class="text-center text-muted-foreground">هیچ کاربری یافت نشد</TableCell>
                        </TableRow>
                        @endforelse
                    </TableBody>
                </Table>
            </CardContent>
        </Card>

        <Card>
            <CardHeader>
                <CardTitle>آخرین تراکنش‌ها</CardTitle>
                <CardDescription>تراکنش‌های اخیر سیستم</CardDescription>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>مبلغ</TableHead>
                            <TableHead>وضعیت</TableHead>
                            <TableHead>تاریخ</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($stats['latestTransactions'] ?? [] as $transaction)
                        <TableRow>
                            <TableCell>{{ number_format($transaction['amount']) }} تومان</TableCell>
                            <TableCell>
                                @php
                                    $variant = \App\Helpers\StatusHelper::getTransactionStatusVariant($transaction['status']);
                                    $label = \App\Helpers\StatusHelper::getTransactionStatusLabel($transaction['status']);
                                @endphp
                                <Badge :variant="$variant">
                                    {{ $label }}
                                </Badge>
                            </TableCell>
                            <TableCell>{{ \Carbon\Carbon::parse($transaction['created_at'])->format('Y/m/d') }}</TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="3" class="text-center text-muted-foreground">هیچ تراکنشی یافت نشد</TableCell>
                        </TableRow>
                        @endforelse
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    </div>
</div>
@endsection

