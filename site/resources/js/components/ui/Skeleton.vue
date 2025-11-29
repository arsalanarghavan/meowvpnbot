<template>
    <div :class="cn('animate-pulse rounded-md bg-muted', $attrs.class)" v-bind="$attrs" />
</template>

<script setup>
import { cn } from '@/utils/cn';
</script>

