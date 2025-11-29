@extends('layouts.app.dashboard')
@section('title', 'مدیریت پنل‌ها')

@section('content')
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold tracking-tight">مدیریت پنل‌ها</h1>
            <p class="text-muted-foreground">مدیریت پنل‌های VPN</p>
        </div>
        <Button as="a" href="{{ route('panels.create') }}">ایجاد پنل جدید</Button>
    </div>

    <Card>
        <CardHeader>
            <CardTitle>لیست پنل‌ها</CardTitle>
            <CardDescription>پنل‌های متصل به سیستم</CardDescription>
        </CardHeader>
        <CardContent>
            <div class="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>نام</TableHead>
                            <TableHead>نوع</TableHead>
                            <TableHead>URL</TableHead>
                            <TableHead>اولویت</TableHead>
                            <TableHead>وضعیت</TableHead>
                            <TableHead>عملیات</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($panels as $panel)
                        <TableRow>
                            <TableCell class="font-medium">{{ $panel['name'] }}</TableCell>
                            <TableCell>
                                <Badge variant="outline">{{ $panel['panel_type'] }}</Badge>
                            </TableCell>
                            <TableCell class="text-sm text-muted-foreground">{{ $panel['api_base_url'] }}</TableCell>
                            <TableCell>{{ $panel['priority'] }}</TableCell>
                            <TableCell>
                                @if($panel['is_active'])
                                    <Badge variant="secondary">فعال</Badge>
                                @else
                                    <Badge variant="destructive">غیرفعال</Badge>
                                @endif
                            </TableCell>
                            <TableCell>
                                <div class="flex gap-2">
                                    <Button variant="ghost" size="sm" as="a" href="{{ route('panels.edit', $panel['id']) }}">
                                        ویرایش
                                    </Button>
                                    <Button 
                                        variant="ghost" 
                                        size="sm"
                                        onclick="togglePanel({{ $panel['id'] }}, {{ $panel['is_active'] ? 'false' : 'true' }})"
                                    >
                                        {{ $panel['is_active'] ? 'غیرفعال' : 'فعال' }}
                                    </Button>
                                </div>
                            </TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="6" class="text-center text-muted-foreground py-8">
                                پنلی یافت نشد
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
function togglePanel(id, status) {
    fetch(`/panels/${id}/toggle`, {
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

