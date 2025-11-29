<template>
    <Tab
        :class="cn(
            'inline-flex items-center justify-center whitespace-nowrap rounded-sm px-3 py-1.5 text-sm font-medium ring-offset-background transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
            selected ? 'bg-background text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground',
            $attrs.class
        )"
        v-bind="$attrs"
    >
        <slot />
    </Tab>
</template>

<script setup>
import { Tab } from '@headlessui/vue';
import { cn } from '@/utils/cn';

defineProps({
    selected: {
        type: Boolean,
        default: false,
    },
});
</script>

