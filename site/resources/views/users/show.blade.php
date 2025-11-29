@extends('layouts.app.dashboard')
@section('title', 'جزئیات کاربر')

@section('content')
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold tracking-tight">جزئیات کاربر</h1>
            <p class="text-muted-foreground">شناسه کاربری: {{ $user['user_id'] }}</p>
        </div>
        <Button variant="outline" as="a" href="{{ route('users.index') }}">بازگشت</Button>
    </div>

    <div class="grid gap-6 md:grid-cols-3">
        <!-- اطلاعات کاربر -->
        <Card class="md:col-span-1">
            <CardHeader>
                <CardTitle>اطلاعات کاربر</CardTitle>
            </CardHeader>
            <CardContent class="space-y-4">
                <div>
                    <Label class="text-xs text-muted-foreground">شناسه کاربری</Label>
                    <p class="text-sm font-medium">{{ $user['user_id'] }}</p>
                </div>
                <Separator />
                <div>
                    <Label class="text-xs text-muted-foreground">نقش</Label>
                    <div class="mt-1">
                        @if($user['role'] == 'admin')
                            <Badge variant="destructive">ادمین</Badge>
                        @elseif($user['role'] == 'marketer')
                            <Badge variant="outline">بازاریاب</Badge>
                        @else
                            <Badge variant="secondary">مشتری</Badge>
                        @endif
                    </div>
                </div>
                <Separator />
                <div>
                    <Label class="text-xs text-muted-foreground">موجودی کیف پول</Label>
                    <p class="text-sm font-medium">{{ number_format($user['wallet_balance']) }} تومان</p>
                </div>
                <Separator />
                <div>
                    <Label class="text-xs text-muted-foreground">موجودی کمیسیون</Label>
                    <p class="text-sm font-medium">{{ number_format($user['commission_balance']) }} تومان</p>
                </div>
                <Separator />
                <div>
                    <Label class="text-xs text-muted-foreground">تاریخ عضویت</Label>
                    <p class="text-sm font-medium">{{ \Carbon\Carbon::parse($user['created_at'])->format('Y/m/d H:i') }}</p>
                </div>
                <Separator />
                <div>
                    <Label class="text-xs text-muted-foreground">وضعیت</Label>
                    <div class="mt-1">
                        @if($user['is_active'])
                            <Badge variant="secondary">فعال</Badge>
                        @else
                            <Badge variant="destructive">مسدود</Badge>
                        @endif
                    </div>
                </div>
                <Separator />
                <div class="space-y-2">
                    <Button variant="outline" class="w-full" onclick="changeRole()">تغییر نقش</Button>
                    <Button variant="outline" class="w-full" onclick="addBalance()">افزایش موجودی</Button>
                    <Button 
                        variant="{{ $user['is_active'] ? 'destructive' : 'default' }}" 
                        class="w-full" 
                        onclick="toggleStatus()"
                    >
                        {{ $user['is_active'] ? 'مسدود کردن' : 'فعال کردن' }}
                    </Button>
                </div>
            </CardContent>
        </Card>

        <!-- سرویس‌ها و تراکنش‌ها -->
        <div class="md:col-span-2 space-y-6">
            <!-- سرویس‌های کاربر -->
            <Card>
                <CardHeader>
                    <CardTitle>سرویس‌های کاربر</CardTitle>
                    <CardDescription>لیست سرویس‌های فعال و منقضی شده</CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>نام کاربری</TableHead>
                                    <TableHead>پلن</TableHead>
                                    <TableHead>تاریخ انقضا</TableHead>
                                    <TableHead>وضعیت</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                @forelse($services as $service)
                                <TableRow>
                                    <TableCell class="font-medium">{{ $service['username_in_panel'] }}</TableCell>
                                    <TableCell>{{ $service['plan_name'] }}</TableCell>
                                    <TableCell>{{ \Carbon\Carbon::parse($service['expire_date'])->format('Y/m/d') }}</TableCell>
                                    <TableCell>
                                        @if($service['is_active'])
                                            <Badge variant="secondary">فعال</Badge>
                                        @else
                                            <Badge variant="destructive">منقضی</Badge>
                                        @endif
                                    </TableCell>
                                </TableRow>
                                @empty
                                <TableRow>
                                    <TableCell colspan="4" class="text-center text-muted-foreground py-8">
                                        سرویسی یافت نشد
                                    </TableCell>
                                </TableRow>
                                @endforelse
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>

            <!-- تراکنش‌های اخیر -->
            <Card>
                <CardHeader>
                    <CardTitle>تراکنش‌های اخیر</CardTitle>
                    <CardDescription>تاریخچه تراکنش‌های کاربر</CardDescription>
                </CardHeader>
                <CardContent>
                    <div class="rounded-md border">
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>مبلغ</TableHead>
                                    <TableHead>نوع</TableHead>
                                    <TableHead>وضعیت</TableHead>
                                    <TableHead>تاریخ</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                @forelse($transactions as $transaction)
                                <TableRow>
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
                                    <TableCell>{{ \Carbon\Carbon::parse($transaction['created_at'])->format('Y/m/d H:i') }}</TableCell>
                                </TableRow>
                                @empty
                                <TableRow>
                                    <TableCell colspan="4" class="text-center text-muted-foreground py-8">
                                        تراکنشی یافت نشد
                                    </TableCell>
                                </TableRow>
                                @endforelse
                            </TableBody>
                        </Table>
                    </div>
                </CardContent>
            </Card>
        </div>
    </div>
</div>
@endsection

@section('scripts')
<script>
const userId = {{ $user['user_id'] }};
const updateUrl = "{{ route('users.update', $user['user_id']) }}";

function changeRole() {
    // استفاده از Dialog component برای تغییر نقش
    // در اینجا می‌توان از SweetAlert یا Dialog component استفاده کرد
    const role = prompt('نقش جدید را انتخاب کنید:\n1. customer\n2. marketer\n3. admin');
    if (!role) return;
    
    fetch(updateUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({
            action: 'change_role',
            role: role
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('نقش کاربر با موفقیت تغییر کرد');
            location.reload();
        } else {
            alert(data.message || 'خطایی رخ داد');
        }
    })
    .catch(error => {
        alert('خطا در ارتباط با سرور');
    });
}

function addBalance() {
    const amount = prompt('مبلغ مورد نظر را وارد کنید (تومان):');
    if (!amount || parseFloat(amount) <= 0) return;
    
    fetch(updateUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({
            action: 'add_balance',
            amount: parseFloat(amount)
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`موجودی کاربر ${parseFloat(amount).toLocaleString()} تومان افزایش یافت`);
            location.reload();
        } else {
            alert(data.message || 'خطایی رخ داد');
        }
    })
    .catch(error => {
        alert('خطا در ارتباط با سرور');
    });
}

function toggleStatus() {
    const currentStatus = {{ $user['is_active'] ? 'true' : 'false' }};
    const statusText = currentStatus ? 'مسدود' : 'فعال';
    
    if (!confirm(`آیا مطمئن هستید که می‌خواهید کاربر را ${statusText} کنید؟`)) return;
    
    fetch(updateUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({
            action: 'toggle_status'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`وضعیت کاربر با موفقیت ${statusText} شد`);
            location.reload();
        } else {
            alert(data.message || 'خطایی رخ داد');
        }
    })
    .catch(error => {
        alert('خطا در ارتباط با سرور');
    });
}
</script>
@endsection

