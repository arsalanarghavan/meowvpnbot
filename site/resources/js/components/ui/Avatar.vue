<template>
    <div :class="cn('relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full', $attrs.class)" v-bind="$attrs">
        <img v-if="src" :src="src" :alt="alt" class="aspect-square h-full w-full" />
        <div v-else class="flex h-full w-full items-center justify-center bg-muted">
            <slot name="fallback">
                <span class="text-sm font-medium">{{ initials }}</span>
            </slot>
        </div>
    </div>
</template>

<script setup>
import { computed } from 'vue';
import { cn } from '@/utils/cn';

const props = defineProps({
    src: {
        type: String,
        default: null,
    },
    alt: {
        type: String,
        default: '',
    },
    name: {
        type: String,
        default: '',
    },
});

const initials = computed(() => {
    if (!props.name) return '?';
    const parts = props.name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return parts[0][0].toUpperCase();
});
</script>

