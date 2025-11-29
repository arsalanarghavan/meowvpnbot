<template>
    <div :class="cn('flex flex-col space-y-1.5 text-center sm:text-left', $attrs.class)" v-bind="$attrs">
        <slot />
    </div>
</template>

<script setup>
import { cn } from '@/utils/cn';
</script>

