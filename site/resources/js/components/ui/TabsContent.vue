<template>
    <TabPanel :class="cn('mt-2 ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2', $attrs.class)" v-bind="$attrs">
        <slot />
    </TabPanel>
</template>

<script setup>
import { TabPanel } from '@headlessui/vue';
import { cn } from '@/utils/cn';
</script>

