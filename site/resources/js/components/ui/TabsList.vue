<template>
    <TabList :class="cn('inline-flex h-10 items-center justify-center rounded-md bg-muted p-1 text-muted-foreground', $attrs.class)" v-bind="$attrs">
        <slot />
    </TabList>
</template>

<script setup>
import { TabList } from '@headlessui/vue';
import { cn } from '@/utils/cn';
</script>

