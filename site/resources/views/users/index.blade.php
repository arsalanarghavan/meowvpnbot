@extends('layouts.app.dashboard')
@section('title', 'مدیریت کاربران')

@section('content')
<div class="space-y-6">
    <div class="flex items-center justify-between">
        <div>
            <h1 class="text-3xl font-bold tracking-tight">مدیریت کاربران</h1>
            <p class="text-muted-foreground">مدیریت و مشاهده کاربران سیستم</p>
        </div>
    </div>

    <!-- آمار -->
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
                <div class="text-2xl font-bold">{{ number_format($stats['total']) }}</div>
            </CardContent>
        </Card>

        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">کاربران فعال</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                    <polyline points="22 4 12 14.01 9 11.01"></polyline>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['active']) }}</div>
            </CardContent>
        </Card>

        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">بازاریاب‌ها</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                    <circle cx="9" cy="7" r="4"></circle>
                    <path d="M23 21v-2a4 4 0 0 0-3-3"></path>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['marketers']) }}</div>
            </CardContent>
        </Card>

        <Card>
            <CardHeader class="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle class="text-sm font-medium">ادمین‌ها</CardTitle>
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" class="h-4 w-4 text-muted-foreground">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                </svg>
            </CardHeader>
            <CardContent>
                <div class="text-2xl font-bold">{{ number_format($stats['admins']) }}</div>
            </CardContent>
        </Card>
    </div>

    <!-- فیلترها و جستجو -->
    <Card>
        <CardHeader>
            <CardTitle>لیست کاربران</CardTitle>
            <CardDescription>جستجو و فیلتر کاربران</CardDescription>
        </CardHeader>
        <CardContent>
            <form method="GET" class="flex flex-col md:flex-row gap-4 mb-6">
                <div class="flex-1">
                    <Input
                        type="text"
                        name="search"
                        placeholder="جستجو بر اساس شناسه کاربری..."
                        value="{{ request('search') }}"
                    />
                </div>
                <div class="w-full md:w-48">
                    <Select name="role">
                        <option value="all">همه نقش‌ها</option>
                        <option value="customer" {{ request('role') == 'customer' ? 'selected' : '' }}>مشتری</option>
                        <option value="marketer" {{ request('role') == 'marketer' ? 'selected' : '' }}>بازاریاب</option>
                        <option value="admin" {{ request('role') == 'admin' ? 'selected' : '' }}>ادمین</option>
                    </Select>
                </div>
                <div class="w-full md:w-48">
                    <Select name="status">
                        <option value="all">همه وضعیت‌ها</option>
                        <option value="active" {{ request('status') == 'active' ? 'selected' : '' }}>فعال</option>
                        <option value="blocked" {{ request('status') == 'blocked' ? 'selected' : '' }}>مسدود</option>
                    </Select>
                </div>
                <Button type="submit">جستجو</Button>
            </form>

            <div class="rounded-md border">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>شناسه کاربری</TableHead>
                            <TableHead>نقش</TableHead>
                            <TableHead>موجودی کیف پول</TableHead>
                            <TableHead>موجودی کمیسیون</TableHead>
                            <TableHead>تاریخ عضویت</TableHead>
                            <TableHead>وضعیت</TableHead>
                            <TableHead>عملیات</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        @forelse($users as $user)
                        <TableRow>
                            <TableCell>
                                <a href="{{ route('users.show', $user['user_id']) }}" class="font-medium text-primary hover:underline">
                                    {{ $user['user_id'] }}
                                </a>
                            </TableCell>
                            <TableCell>
                                @if($user['role'] == 'customer')
                                    <Badge variant="secondary">مشتری</Badge>
                                @elseif($user['role'] == 'marketer')
                                    <Badge variant="outline">بازاریاب</Badge>
                                @else
                                    <Badge variant="destructive">ادمین</Badge>
                                @endif
                            </TableCell>
                            <TableCell>{{ number_format($user['wallet_balance']) }} تومان</TableCell>
                            <TableCell>{{ number_format($user['commission_balance']) }} تومان</TableCell>
                            <TableCell>{{ \Carbon\Carbon::parse($user['created_at'])->format('Y/m/d H:i') }}</TableCell>
                            <TableCell>
                                @if($user['is_active'])
                                    <Badge variant="secondary">فعال</Badge>
                                @else
                                    <Badge variant="destructive">مسدود</Badge>
                                @endif
                            </TableCell>
                            <TableCell>
                                <Button variant="ghost" size="sm" as="a" href="{{ route('users.show', $user['user_id']) }}">
                                    مشاهده
                                </Button>
                            </TableCell>
                        </TableRow>
                        @empty
                        <TableRow>
                            <TableCell colspan="7" class="text-center text-muted-foreground py-8">
                                کاربری یافت نشد
                            </TableCell>
                        </TableRow>
                        @endforelse
                    </TableBody>
                </Table>
            </div>

            @if(method_exists($users, 'links'))
            <div class="mt-4">
                {{ $users->links() }}
            </div>
            @endif
        </CardContent>
    </Card>
</div>
@endsection

