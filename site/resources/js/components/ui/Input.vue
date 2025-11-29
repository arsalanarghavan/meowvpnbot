<template>
    <input
        :type="type"
        :class="cn(
            'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
            error && 'border-destructive focus-visible:ring-destructive',
            $attrs.class
        )"
        v-bind="$attrs"
    />
    <p v-if="error" class="mt-1 text-sm text-destructive">{{ error }}</p>
</template>

<script setup>
import { cn } from '@/utils/cn';

defineProps({
    type: {
        type: String,
        default: 'text',
    },
    error: {
        type: String,
        default: null,
    },
});
</script>

