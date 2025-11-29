<template>
    <div
        :class="cn(
            'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
            variants[variant],
            $attrs.class
        )"
        v-bind="$attrs"
    >
        <slot />
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { cn } from '@/utils/cn';

const props = defineProps({
    variant: {
        type: String,
        default: 'default',
        validator: (value) => ['default', 'secondary', 'destructive', 'outline'].includes(value),
    },
});

const variants = {
    default: 'border-transparent bg-primary text-primary-foreground hover:bg-primary/80',
    secondary: 'border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80',
    destructive:
        'border-transparent bg-destructive text-destructive-foreground hover:bg-destructive/80',
    outline: 'text-foreground',
};
</script>

