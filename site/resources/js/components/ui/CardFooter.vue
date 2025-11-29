<template>
    <div :class="cn('flex items-center p-6 pt-0', $attrs.class)">
        <slot />
    </div>
</template>

<script setup>
import { cn } from '@/utils/cn';
</script>

