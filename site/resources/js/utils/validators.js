export function required(value) {
    return value !== null && value !== undefined && value !== '' && String(value).trim() !== '';
}

export function email(value) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value);
}

export function minLength(value, min) {
    return String(value).length >= min;
}

export function maxLength(value, max) {
    return String(value).length <= max;
}

export function numeric(value) {
    return !isNaN(value) && !isNaN(parseFloat(value));
}

export function phone(value) {
    const phoneRegex = /^09\d{9}$/;
    return phoneRegex.test(value);
}

export function validate(value, rules) {
    for (const rule of rules) {
        if (typeof rule === 'function') {
            if (!rule(value)) return false;
        } else if (typeof rule === 'object') {
            const { validator, message } = rule;
            if (!validator(value)) {
                return { valid: false, message };
            }
        }
    }
    return { valid: true };
}

/**
 * Sanitizes input to prevent XSS attacks
 * @param {string} input - Input string to sanitize
 * @returns {string} - Sanitized string
 */
export function sanitizeInput(input) {
    if (typeof input !== 'string') {
        return '';
    }
    
    // Remove null bytes and control characters
    let sanitized = input.replace(/[\x00-\x1F\x7F]/g, '');
    
    // Remove potentially dangerous HTML/script tags
    const div = document.createElement('div');
    div.textContent = sanitized;
    sanitized = div.innerHTML;
    
    // Decode HTML entities back to plain text
    const txt = document.createElement('textarea');
    txt.innerHTML = sanitized;
    sanitized = txt.value;
    
    return sanitized.trim();
}

/**
 * Sanitizes an object by sanitizing all string values
 * @param {object} obj - Object to sanitize
 * @returns {object} - Sanitized object
 */
export function sanitizeObject(obj) {
    if (typeof obj !== 'object' || obj === null) {
        return obj;
    }
    
    const sanitized = Array.isArray(obj) ? [] : {};
    
    for (const key in obj) {
        if (Object.prototype.hasOwnProperty.call(obj, key)) {
            const value = obj[key];
            if (typeof value === 'string') {
                sanitized[key] = sanitizeInput(value);
            } else if (typeof value === 'object' && value !== null) {
                sanitized[key] = sanitizeObject(value);
            } else {
                sanitized[key] = value;
            }
        }
    }
    
    return sanitized;
}

/**
 * Validates and sanitizes a number input
 * @param {string|number} value - Value to validate
 * @param {number} min - Minimum value
 * @param {number} max - Maximum value
 * @returns {number|null} - Validated number or null
 */
export function validateNumber(value, min = -Infinity, max = Infinity) {
    const num = typeof value === 'string' ? parseFloat(value) : value;
    if (isNaN(num) || num < min || num > max) {
        return null;
    }
    return num;
}

/**
 * Validates a user ID
 * @param {string|number} value - User ID to validate
 * @returns {number|null} - Validated user ID or null
 */
export function validateUserId(value) {
    const id = typeof value === 'string' ? parseInt(value, 10) : value;
    if (isNaN(id) || id <= 0 || !Number.isInteger(id)) {
        return null;
    }
    return id;
}

