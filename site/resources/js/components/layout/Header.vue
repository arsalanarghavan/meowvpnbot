<template>
    <header class="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div class="container flex h-14 items-center">
            <div class="mr-4 hidden md:flex">
                <a class="mr-6 flex items-center space-x-2" href="/">
                    <span class="font-bold">🐱 MeowVPN</span>
                </a>
            </div>
            <div class="flex flex-1 items-center justify-between space-x-2 md:justify-end">
                <div class="w-full flex-1 md:w-auto md:flex-none"></div>
                <nav class="flex items-center space-x-2">
                    <DropdownMenu>
                        <template #trigger>
                            <Button variant="ghost" size="icon" class="h-9 w-9 rounded-full">
                                <Avatar name="Admin" />
                            </Button>
                        </template>
                        <DropdownMenuItem>
                            <a href="/settings" class="w-full">تنظیمات</a>
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                            <form method="POST" action="/logout" class="w-full">
                                <button type="submit" class="w-full text-right">خروج</button>
                            </form>
                        </DropdownMenuItem>
                    </DropdownMenu>
                </nav>
            </div>
        </div>
    </header>
</template>

<script setup>
import Button from '../ui/Button.vue';
import Avatar from '../ui/Avatar.vue';
import DropdownMenu from '../ui/DropdownMenu.vue';
import DropdownMenuItem from '../ui/DropdownMenuItem.vue';
</script>

