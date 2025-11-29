import './bootstrap';
import { createApp } from 'vue';

// Import utilities
import { cn } from './utils/cn';

// Make cn available globally
window.cn = cn;

// Import components
import AppLayout from './components/layout/AppLayout.vue';
import Header from './components/layout/Header.vue';
import Sidebar from './components/layout/Sidebar.vue';

// Auto-import UI components
const componentFiles = import.meta.glob('./components/ui/**/*.vue', { eager: true });

// Create app instance
const app = createApp({});

// Register layout components
app.component('AppLayout', AppLayout);
app.component('Header', Header);
app.component('Sidebar', Sidebar);

// Register UI components
Object.entries(componentFiles).forEach(([path, module]) => {
    const componentName = path
        .split('/')
        .pop()
        .replace(/\.\w+$/, '');
    
    if (module.default) {
        app.component(componentName, module.default);
    }
});

// Mount app to #app element or elements with data-vue attribute
document.addEventListener('DOMContentLoaded', () => {
    // Check if there's a #app element with data-vue attribute
    const appElement = document.getElementById('app');
    if (appElement && appElement.hasAttribute('data-vue')) {
        const componentName = appElement.getAttribute('data-vue');
        const component = app._context.components[componentName];
        if (component) {
            app.mount('#app');
        } else {
            // If component not found, mount empty app
            app.mount('#app');
        }
    } else {
        // Mount to #app if it exists, otherwise look for data-vue elements
        if (appElement) {
            app.mount('#app');
        } else {
            // Fallback: mount to elements with data-vue attribute
            const vueElements = document.querySelectorAll('[data-vue]');
            vueElements.forEach((el) => {
                const componentName = el.getAttribute('data-vue');
                const component = app._context.components[componentName];
                if (component) {
                    createApp(component).mount(el);
                }
            });
        }
    }
});

export default app;
