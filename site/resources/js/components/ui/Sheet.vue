<template>
    <Teleport to="body">
        <TransitionRoot appear :show="modelValue" as="template">
            <Dialog as="div" @close="close" class="relative z-50">
                <TransitionChild
                    as="template"
                    enter="ease-in-out duration-500"
                    enter-from="opacity-0"
                    enter-to="opacity-100"
                    leave="ease-in-out duration-500"
                    leave-from="opacity-100"
                    leave-to="opacity-0"
                >
                    <div class="fixed inset-0 bg-black/80 transition-opacity" />
                </TransitionChild>

                <div class="fixed inset-0 overflow-hidden">
                    <div class="absolute inset-0 overflow-hidden">
                        <div 
                            :class="cn(
                                'pointer-events-none fixed inset-y-0 flex max-w-full',
                                side === 'right' ? 'right-0' : 'left-0'
                            )"
                        >
                            <TransitionChild
                                as="template"
                                enter="transform transition ease-in-out duration-500"
                                :enter-from="side === 'right' ? 'translate-x-full' : '-translate-x-full'"
                                enter-to="translate-x-0"
                                leave="transform transition ease-in-out duration-500"
                                leave-from="translate-x-0"
                                :leave-to="side === 'right' ? 'translate-x-full' : '-translate-x-full'"
                            >
                                <DialogPanel
                                    :class="cn(
                                        'pointer-events-auto w-screen max-w-sm',
                                        $attrs.class
                                    )"
                                >
                                    <div class="flex h-full flex-col overflow-y-scroll bg-background py-6 shadow-xl">
                                        <slot />
                                    </div>
                                </DialogPanel>
                            </TransitionChild>
                        </div>
                    </div>
                </div>
            </Dialog>
        </TransitionRoot>
    </Teleport>
</template>

<script setup>
import { Dialog, DialogPanel, TransitionChild, TransitionRoot } from '@headlessui/vue';
import { cn } from '@/utils/cn';

const props = defineProps({
    modelValue: {
        type: Boolean,
        default: false,
    },
    side: {
        type: String,
        default: 'right',
        validator: (value) => ['left', 'right', 'top', 'bottom'].includes(value),
    },
});

const emit = defineEmits(['update:modelValue']);

const close = () => {
    emit('update:modelValue', false);
};
</script>

