<template>
    <div
        :class="cn(
            'relative w-full rounded-lg border p-4 [&>svg~*]:pl-7 [&>svg+div]:translate-y-[-3px] [&>svg]:absolute [&>svg]:left-4 [&>svg]:top-4 [&>svg]:text-foreground',
            variants[variant],
            $attrs.class
        )"
        v-bind="$attrs"
    >
        <slot />
    </div>
</template>

<script setup>
import { cn } from '@/utils/cn';

const props = defineProps({
    variant: {
        type: String,
        default: 'default',
        validator: (value) => ['default', 'destructive'].includes(value),
    },
});

const variants = {
    default: 'bg-background text-foreground',
    destructive: 'border-destructive/50 text-destructive dark:border-destructive [&>svg]:text-destructive',
};
</script>

