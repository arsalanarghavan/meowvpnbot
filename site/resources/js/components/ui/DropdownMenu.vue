<template>
    <Menu as="div" class="relative inline-block text-left">
        <MenuButton :as="as" :class="cn('inline-flex items-center', $attrs.class)" v-bind="$attrs">
            <slot name="trigger" />
        </MenuButton>

        <Transition
            enter-active-class="transition duration-100 ease-out"
            enter-from-class="transform scale-95 opacity-0"
            enter-to-class="transform scale-100 opacity-100"
            leave-active-class="transition duration-75 ease-in"
            leave-from-class="transform scale-100 opacity-100"
            leave-to-class="transform scale-95 opacity-0"
        >
            <MenuItems
                :class="cn(
                    'absolute right-0 mt-2 w-56 origin-top-right divide-y divide-gray-100 rounded-md bg-background shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none z-50',
                    $attrs.class
                )"
            >
                <div class="px-1 py-1">
                    <slot />
                </div>
            </MenuItems>
        </Transition>
    </Menu>
</template>

<script setup>
import { Transition } from 'vue';
import { Menu, MenuButton, MenuItems, MenuItem } from '@headlessui/vue';
import { cn } from '@/utils/cn';

defineProps({
    as: {
        type: String,
        default: 'button',
    },
});
</script>

