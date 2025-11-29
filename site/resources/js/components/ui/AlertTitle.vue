<template>
    <h5 :class="cn('mb-1 font-medium leading-none tracking-tight', $attrs.class)" v-bind="$attrs">
        <slot />
    </h5>
</template>

<script setup>
import { cn } from '@/utils/cn';
</script>

