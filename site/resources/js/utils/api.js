import axios from 'axios';
import { sanitizeObject } from './validators';

const api = axios.create({
    baseURL: '/api',
    headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
    },
});

// Add CSRF token to requests
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
if (csrfToken) {
    api.defaults.headers.common['X-CSRF-TOKEN'] = csrfToken;
}

// Request interceptor - sanitize request data
api.interceptors.request.use(
    (config) => {
        // Sanitize request data
        if (config.data && typeof config.data === 'object') {
            config.data = sanitizeObject(config.data);
        }
        
        // Sanitize URL parameters
        if (config.params && typeof config.params === 'object') {
            config.params = sanitizeObject(config.params);
        }
        
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// Response interceptor
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            // Redirect to login
            window.location.href = '/login';
        }
        
        // Sanitize error messages before displaying
        if (error.response?.data?.message) {
            error.response.data.message = sanitizeObject(error.response.data.message);
        }
        
        return Promise.reject(error);
    }
);

export default api;

