<template>
    <div class="min-h-screen bg-background">
        <Header />
        <div class="flex">
            <Sidebar />
            <main class="flex-1 p-6">
                <slot />
            </main>
        </div>
    </div>
</template>

<script setup>
import Header from './Header.vue';
import Sidebar from './Sidebar.vue';
</script>

