@extends('layouts.app.dashboard')
@section('title', 'کارت‌های بانکی')

@section('content')
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold tracking-tight">کارت‌های بانکی</h1>
            <p class="text-muted-foreground">مدیریت کارت‌های بانکی برای پرداخت</p>
        </div>
        <Button as="a" href="{{ route('card-accounts.create') }}">افزودن کارت جدید</Button>
    </div>

    <!-- آمار -->
    <div class="grid gap-4 md:grid-cols-3">
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">کل کارت‌ها</CardTitle>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['total'] ?? 0) }}</div>
            </CardContent>
        </Card>
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">کارت‌های فعال</CardTitle>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['active'] ?? 0) }}</div>
            </CardContent>
        </Card>
        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">دریافتی امروز</CardTitle>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['today_received'] ?? 0) }} تومان</div>
            </CardContent>
        </Card>
    </div>

    <!-- لیست کارت‌ها -->
    <Card>
        <CardHeader>
            <CardTitle>لیست کارت‌های بانکی</CardTitle>
            <CardDescription>کارت‌های ثبت شده برای دریافت پرداخت</CardDescription>
        </CardHeader>
        <CardContent>
            <div class="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>نام صاحب کارت</TableHead>
                            <TableHead>شماره کارت</TableHead>
                            <TableHead>محدودیت روزانه</TableHead>
                            <TableHead>دریافتی امروز</TableHead>
                            <TableHead>اولویت</TableHead>
                            <TableHead>وضعیت</TableHead>
                            <TableHead>عملیات</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($cards as $card)
                        <TableRow>
                            <TableCell class="font-medium">{{ $card['card_holder_name'] }}</TableCell>
                            <TableCell class="font-mono">{{ $card['card_number'] }}</TableCell>
                            <TableCell>{{ number_format($card['daily_limit']) }} تومان</TableCell>
                            <TableCell>{{ number_format($card['today_received'] ?? 0) }} تومان</TableCell>
                            <TableCell>{{ $card['priority'] }}</TableCell>
                            <TableCell>
                                @if($card['is_active'])
                                    <Badge variant="secondary">فعال</Badge>
                                @else
                                    <Badge variant="destructive">غیرفعال</Badge>
                                @endif
                            </TableCell>
                            <TableCell>
                                <div class="flex gap-2">
                                    <Button variant="ghost" size="sm" as="a" href="{{ route('card-accounts.edit', $card['id']) }}">
                                        ویرایش
                                    </Button>
                                    <Button 
                                        variant="ghost" 
                                        size="sm"
                                        onclick="toggleCard({{ $card['id'] }}, {{ $card['is_active'] ? 'false' : 'true' }})"
                                    >
                                        {{ $card['is_active'] ? 'غیرفعال' : 'فعال' }}
                                    </Button>
                                </div>
                            </TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="7" class="text-center text-muted-foreground py-8">
                                کارت بانکی یافت نشد
                            </TableCell>
                        </TableRow>
                        @endforelse
                    </TableBody>
                </Table>
            </div>
        </CardContent>
    </Card>
</div>

@push('scripts')
<script>
function toggleCard(id, status) {
    fetch(`/card-accounts/${id}/toggle`, {
        method: 'POST',
        headers: {
            'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify({ is_active: status })
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

