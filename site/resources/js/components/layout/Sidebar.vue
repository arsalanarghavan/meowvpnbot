<template>
    <aside class="hidden w-64 border-r bg-background md:block">
        <nav class="space-y-1 p-4">
            <a
                v-for="item in navigation"
                :key="item.name"
                :href="item.href"
                :class="cn(
                    'flex items-center rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive(item.href)
                        ? 'bg-accent text-accent-foreground'
                        : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                )"
            >
                <span class="ml-2">{{ item.icon }}</span>
                {{ item.name }}
            </a>
        </nav>
    </aside>
</template>

<script setup>
import { computed } from 'vue';
import { cn } from '@/utils/cn';

const navigation = [
    { name: 'داشبورد', href: '/dashboard', icon: '🏠' },
    { name: 'کاربران', href: '/users', icon: '👥' },
    { name: 'پلن‌ها', href: '/plans', icon: '📦' },
    { name: 'پنل‌ها', href: '/panels', icon: '🖥️' },
    { name: 'تراکنش‌ها', href: '/transactions', icon: '💳' },
    { name: 'بازاریاب‌ها', href: '/marketers', icon: '📊' },
    { name: 'کارت‌های هدیه', href: '/gift-cards', icon: '🎁' },
    { name: 'کارت‌های بانکی', href: '/card-accounts', icon: '🏦' },
    { name: 'تنظیمات', href: '/settings', icon: '⚙️' },
];

const currentPath = computed(() => {
    if (typeof window !== 'undefined') {
        return window.location.pathname;
    }
    return '';
});

const isActive = (href) => {
    const path = currentPath.value;
    return path === href || path.startsWith(href + '/');
};
</script>

