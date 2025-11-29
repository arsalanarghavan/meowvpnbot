<template>
    <div v-if="hasError" class="error-boundary">
        <div class="error-content">
            <h2>خطایی رخ داد</h2>
            <p>{{ errorMessage }}</p>
            <button @click="resetError" class="btn btn-primary">تلاش مجدد</button>
        </div>
    </div>
    <slot v-else />
</template>

<script>
import { defineComponent, ref, onErrorCaptured } from 'vue';

export default defineComponent({
    name: 'ErrorBoundary',
    setup(_, { slots }) {
        const hasError = ref(false);
        const errorMessage = ref('');

        onErrorCaptured((err, instance, info) => {
            console.error('Error caught by boundary:', err, info);
            hasError.value = true;
            errorMessage.value = err.message || 'یک خطای غیرمنتظره رخ داد';
            
            // Log error to console in development
            if (import.meta.env.DEV) {
                console.error('Component:', instance);
                console.error('Error info:', info);
            }
            
            return false; // Prevent error from propagating
        });

        const resetError = () => {
            hasError.value = false;
            errorMessage.value = '';
        };

        return {
            hasError,
            errorMessage,
            resetError
        };
    }
});
</script>

<style scoped>
.error-boundary {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 200px;
    padding: 2rem;
}

.error-content {
    text-align: center;
    max-width: 500px;
}

.error-content h2 {
    color: #dc3545;
    margin-bottom: 1rem;
}

.error-content p {
    color: #6c757d;
    margin-bottom: 1.5rem;
}
</style>

