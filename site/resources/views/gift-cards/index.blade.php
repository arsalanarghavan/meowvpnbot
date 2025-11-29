@extends('layouts.app.dashboard')
@section('title', 'کارت‌های هدیه')

@section('content')
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold tracking-tight">کارت‌های هدیه</h1>
            <p class="text-muted-foreground">مدیریت کارت‌های هدیه</p>
        </div>
        <Button as="a" href="{{ route('gift-cards.create') }}">ایجاد کارت هدیه</Button>
    </div>

    <!-- فیلترها -->
    <Card>
        <CardHeader>
            <CardTitle>فیلترها</CardTitle>
        </CardHeader>
        <CardContent>
            <form method="GET" class="flex gap-4">
                <div class="w-full md:w-48">
                    <Select name="status">
                        <option value="all">همه وضعیت‌ها</option>
                        <option value="active" {{ request('status') == 'active' ? 'selected' : '' }}>فعال</option>
                        <option value="used" {{ request('status') == 'used' ? 'selected' : '' }}>استفاده شده</option>
                        <option value="expired" {{ request('status') == 'expired' ? 'selected' : '' }}>منقضی شده</option>
                    </Select>
                </div>
                <Button type="submit">فیلتر</Button>
            </form>
        </CardContent>
    </Card>

    <!-- لیست کارت‌ها -->
    <Card>
        <CardHeader>
            <CardTitle>لیست کارت‌های هدیه</CardTitle>
            <CardDescription>کارت‌های هدیه ایجاد شده</CardDescription>
        </CardHeader>
        <CardContent>
            <div class="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>کد</TableHead>
                            <TableHead>مبلغ</TableHead>
                            <TableHead>وضعیت</TableHead>
                            <TableHead>تاریخ ایجاد</TableHead>
                            <TableHead>تاریخ انقضا</TableHead>
                            <TableHead>عملیات</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($giftCards as $card)
                        <TableRow>
                            <TableCell class="font-mono">{{ $card['code'] }}</TableCell>
                            <TableCell class="font-medium">{{ number_format($card['amount']) }} تومان</TableCell>
                            <TableCell>
                                @if($card['is_used'])
                                    <Badge variant="destructive">استفاده شده</Badge>
                                @elseif($card['expires_at'] && \Carbon\Carbon::parse($card['expires_at'])->isPast())
                                    <Badge variant="destructive">منقضی شده</Badge>
                                @else
                                    <Badge variant="secondary">فعال</Badge>
                                @endif
                            </TableCell>
                            <TableCell class="text-sm text-muted-foreground">
                                {{ \Carbon\Carbon::parse($card['created_at'])->format('Y/m/d') }}
                            </TableCell>
                            <TableCell class="text-sm text-muted-foreground">
                                {{ $card['expires_at'] ? \Carbon\Carbon::parse($card['expires_at'])->format('Y/m/d') : '-' }}
                            </TableCell>
                            <TableCell>
                                <Button 
                                    variant="destructive" 
                                    size="sm"
                                    onclick="deleteCard({{ $card['id'] }})"
                                >
                                    حذف
                                </Button>
                            </TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="6" class="text-center text-muted-foreground py-8">
                                کارت هدیه‌ای یافت نشد
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
function deleteCard(id) {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این کارت هدیه را حذف کنید؟')) return;
    
    fetch(`/gift-cards/${id}`, {
        method: 'DELETE',
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

