@extends('layouts.app.dashboard')
@section('title', 'مدیریت پلن‌ها')

@section('content')
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold tracking-tight">مدیریت پلن‌ها</h1>
            <p class="text-muted-foreground">مدیریت پلن‌های VPN</p>
        </div>
        <Button as="a" href="{{ route('plans.create') }}">ایجاد پلن جدید</Button>
    </div>

    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        @forelse($plans as $plan)
        <Card>
            <CardHeader>
                <div class="flex items-center justify-between">
                    <CardTitle>{{ $plan['name'] }}</CardTitle>
                    <Badge variant="outline">{{ $plan['category'] }}</Badge>
                </div>
                <CardDescription>
                    {{ $plan['duration_days'] }} روز - {{ $plan['traffic_gb'] }} گیگابایت
                </CardDescription>
            </CardHeader>
            <CardContent>
                <div class="space-y-4">
                    <div>
                        <Label class="text-xs text-muted-foreground">قیمت</Label>
                        <p class="text-2xl font-bold">{{ number_format($plan['price']) }} تومان</p>
                    </div>
                    <Separator />
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <Label class="text-xs text-muted-foreground">تعداد سرویس</Label>
                            <p class="font-medium">{{ number_format($plan['services_count'] ?? 0) }}</p>
                        </div>
                        <div>
                            <Label class="text-xs text-muted-foreground">سرویس فعال</Label>
                            <p class="font-medium">{{ number_format($plan['active_services_count'] ?? 0) }}</p>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <Button variant="outline" size="sm" class="flex-1" as="a" href="{{ route('plans.edit', $plan['id']) }}">
                            ویرایش
                        </Button>
                        <Button variant="destructive" size="sm" class="flex-1" onclick="deletePlan({{ $plan['id'] }})">
                            حذف
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
        @empty
        <Card class="md:col-span-3">
            <CardContent class="py-12 text-center">
                <p class="text-muted-foreground">هیچ پلنی یافت نشد</p>
                <Button variant="outline" class="mt-4" as="a" href="{{ route('plans.create') }}">ایجاد اولین پلن</Button>
            </CardContent>
        </Card>
        @endforelse
    </div>
</div>

@push('scripts')
<script>
function deletePlan(id) {
    if (!confirm('آیا مطمئن هستید که می‌خواهید این پلن را حذف کنید؟')) return;
    
    fetch(`/plans/${id}`, {
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

