<template>
    <Teleport to="body">
        <TransitionRoot appear :show="modelValue" as="template">
            <Dialog as="div" @close="close" class="relative z-50">
                <TransitionChild
                    as="template"
                    enter="duration-300 ease-out"
                    enter-from="opacity-0"
                    enter-to="opacity-100"
                    leave="duration-200 ease-in"
                    leave-from="opacity-100"
                    leave-to="opacity-0"
                >
                    <div class="fixed inset-0 bg-black/80" />
                </TransitionChild>

                <div class="fixed inset-0 flex items-center justify-center p-4">
                    <TransitionChild
                        as="template"
                        enter="duration-300 ease-out"
                        enter-from="opacity-0 scale-95"
                        enter-to="opacity-100 scale-100"
                        leave="duration-200 ease-in"
                        leave-from="opacity-100 scale-100"
                        leave-to="opacity-0 scale-95"
                    >
                        <DialogPanel
                            :class="cn(
                                'w-full max-w-lg transform overflow-hidden rounded-2xl bg-background p-6 text-left align-middle shadow-xl transition-all',
                                $attrs.class
                            )"
                        >
                            <slot />
                        </DialogPanel>
                    </TransitionChild>
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
});

const emit = defineEmits(['update:modelValue']);

const close = () => {
    emit('update:modelValue', false);
};
</script>

