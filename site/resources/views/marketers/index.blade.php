@extends('layouts.app.dashboard')
@section('title', 'بازاریاب‌ها')

@section('content')
<div class="space-y-6">
    <div>
        <h1 class="text-3xl font-bold tracking-tight">بازاریاب‌ها</h1>
        <p class="text-muted-foreground">مدیریت بازاریاب‌ها و کمیسیون‌ها</p>
    </div>

    <Card>
        <CardHeader>
            <CardTitle>لیست بازاریاب‌ها</CardTitle>
            <CardDescription>بازاریاب‌های ثبت‌نام شده در سیستم</CardDescription>
        </CardHeader>
        <CardContent>
            <div class="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>شناسه کاربری</TableHead>
                            <TableHead>موجودی کمیسیون</TableHead>
                            <TableHead>تعداد زیرمجموعه</TableHead>
                            <TableHead>تاریخ عضویت</TableHead>
                            <TableHead>عملیات</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($marketers as $marketer)
                        <TableRow>
                            <TableCell class="font-medium">{{ $marketer['user_id'] }}</TableCell>
                            <TableCell class="font-medium">{{ number_format($marketer['commission_balance']) }} تومان</TableCell>
                            <TableCell>{{ number_format($marketer['referrals_count'] ?? 0) }}</TableCell>
                            <TableCell class="text-sm text-muted-foreground">
                                {{ \Carbon\Carbon::parse($marketer['created_at'])->format('Y/m/d') }}
                            </TableCell>
                            <TableCell>
                                <Button variant="outline" size="sm" as="a" href="{{ route('marketers.show', $marketer['user_id']) }}">
                                    مشاهده
                                </Button>
                            </TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="5" class="text-center text-muted-foreground py-8">
                                بازاریابی یافت نشد
                            </TableCell>
                        </TableRow>
                        @endforelse
                    </TableBody>
                </Table>
            </div>
        </CardContent>
    </Card>
</div>
@endsection

