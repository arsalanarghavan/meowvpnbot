<template>
    <MenuItem v-slot="{ active }">
        <button
            :class="cn(
                'group flex w-full items-center rounded-md px-2 py-2 text-sm',
                active ? 'bg-accent text-accent-foreground' : 'text-foreground',
                $attrs.class
            )"
            v-bind="$attrs"
        >
            <slot />
        </button>
    </MenuItem>
</template>

<script setup>
import { MenuItem } from '@headlessui/vue';
import { cn } from '@/utils/cn';
</script>

