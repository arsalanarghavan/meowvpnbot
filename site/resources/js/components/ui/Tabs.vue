<template>
    <TabGroup :selectedIndex="selectedIndex" @change="handleChange">
        <slot />
    </TabGroup>
</template>

<script setup>
import { TabGroup } from '@headlessui/vue';
import { ref, watch } from 'vue';

const props = defineProps({
    modelValue: {
        type: [Number, String],
        default: 0,
    },
    defaultValue: {
        type: [Number, String],
        default: 0,
    },
});

const emit = defineEmits(['update:modelValue']);

const selectedIndex = ref(props.modelValue ?? props.defaultValue);

// Watch for external changes to modelValue
watch(() => props.modelValue, (newValue) => {
    if (newValue !== undefined && newValue !== null) {
        selectedIndex.value = newValue;
    }
});

const handleChange = (index) => {
    selectedIndex.value = index;
    emit('update:modelValue', index);
};
</script>

