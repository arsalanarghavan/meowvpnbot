@extends('layouts.app.dashboard')
@section('title', 'تراکنش‌ها')

@section('content')
<div class="space-y-6">
    <div>
        <h1 class="text-3xl font-bold tracking-tight">تراکنش‌ها</h1>
        <p class="text-muted-foreground">مدیریت و مشاهده تراکنش‌های سیستم</p>
    </div>

    <!-- فیلترها -->
    <Card>
        <CardHeader>
            <CardTitle>فیلترها</CardTitle>
        </CardHeader>
        <CardContent>
            <form method="GET" class="flex flex-col md:flex-row gap-4">
                <div class="flex-1">
                    <Input
                        type="text"
                        name="search"
                        placeholder="جستجو بر اساس کد پیگیری یا شناسه کاربری..."
                        value="{{ request('search') }}"
                    />
                </div>
                <div class="w-full md:w-48">
                    <Select name="status">
                        <option value="all">همه وضعیت‌ها</option>
                        <option value="موفق" {{ request('status') == 'موفق' ? 'selected' : '' }}>موفق</option>
                        <option value="در انتظار" {{ request('status') == 'در انتظار' ? 'selected' : '' }}>در انتظار</option>
                        <option value="ناموفق" {{ request('status') == 'ناموفق' ? 'selected' : '' }}>ناموفق</option>
                    </Select>
                </div>
                <div class="w-full md:w-48">
                    <Select name="type">
                        <option value="all">همه انواع</option>
                        <option value="آنلاین" {{ request('type') == 'آنلاین' ? 'selected' : '' }}>آنلاین</option>
                        <option value="کارت به کارت" {{ request('type') == 'کارت به کارت' ? 'selected' : '' }}>کارت به کارت</option>
                    </Select>
                </div>
                <Button type="submit">جستجو</Button>
            </form>
        </CardContent>
    </Card>

    <!-- لیست تراکنش‌ها -->
    <Card>
        <CardHeader>
            <CardTitle>لیست تراکنش‌ها</CardTitle>
            <CardDescription>تراکنش‌های انجام شده در سیستم</CardDescription>
        </CardHeader>
        <CardContent>
            <div class="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>کد پیگیری</TableHead>
                            <TableHead>کاربر</TableHead>
                            <TableHead>پلن</TableHead>
                            <TableHead>مبلغ</TableHead>
                            <TableHead>نوع</TableHead>
                            <TableHead>وضعیت</TableHead>
                            <TableHead>تاریخ</TableHead>
                            <TableHead>عملیات</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($transactions as $transaction)
                        <TableRow>
                            <TableCell class="font-mono text-sm">{{ $transaction['tracking_code'] ?? '-' }}</TableCell>
                            <TableCell>{{ $transaction['user_id'] ?? '-' }}</TableCell>
                            <TableCell>{{ $transaction['plan_name'] ?? '-' }}</TableCell>
                            <TableCell class="font-medium">{{ number_format($transaction['amount']) }} تومان</TableCell>
                            <TableCell>{{ $transaction['type'] }}</TableCell>
                            <TableCell>
                                @if($transaction['status'] == 'موفق')
                                    <Badge variant="secondary">موفق</Badge>
                                @elseif($transaction['status'] == 'در انتظار')
                                    <Badge variant="outline">در انتظار</Badge>
                                @else
                                    <Badge variant="destructive">ناموفق</Badge>
                                @endif
                            </TableCell>
                            <TableCell class="text-sm text-muted-foreground">
                                {{ \Carbon\Carbon::parse($transaction['created_at'])->format('Y/m/d H:i') }}
                            </TableCell>
                            <TableCell>
                                @if($transaction['status'] == 'در انتظار')
                                    <div class="flex gap-2">
                                        <Button 
                                            variant="outline" 
                                            size="sm"
                                            onclick="approveTransaction({{ $transaction['id'] }})"
                                        >
                                            تایید
                                        </Button>
                                        <Button 
                                            variant="destructive" 
                                            size="sm"
                                            onclick="rejectTransaction({{ $transaction['id'] }})"
                                        >
                                            رد
                                        </Button>
                                    </div>
                                @else
                                    <Button variant="ghost" size="sm" as="a" href="{{ route('transactions.show', $transaction['id']) }}">
                                        مشاهده
                                    </Button>
                                @endif
                            </TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="8" class="text-center text-muted-foreground py-8">
                                تراکنشی یافت نشد
                            </TableCell>
                        </TableRow>
                        @endforelse
                    </TableBody>
                </Table>
            </div>

            @if(method_exists($transactions, 'links'))
            <div class="mt-4">
                {{ $transactions->links() }}
            </div>
            @endif
        </CardContent>
    </Card>
</div>

@push('scripts')
<script>
function approveTransaction(id) {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این تراکنش را تایید کنید؟')) return;
    
    fetch(`/transactions/${id}/approve`, {
        method: 'POST',
        headers: {
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message || 'خطایی رخ داد');
        }
    });
}

function rejectTransaction(id) {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این تراکنش را رد کنید؟')) return;
    
    fetch(`/transactions/${id}/reject`, {
        method: 'POST',
        headers: {
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert(data.message || 'خطایی رخ داد');
        }
    });
}
</script>
@endpush
@endsection

