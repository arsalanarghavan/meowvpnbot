export function formatNumber(num) {
    return new Intl.NumberFormat('fa-IR').format(num);
}

export function formatCurrency(amount) {
    return new Intl.NumberFormat('fa-IR', {
        style: 'currency',
        currency: 'IRR',
        minimumFractionDigits: 0,
    }).format(amount);
}

export function formatDate(date) {
    return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
    }).format(new Date(date));
}

export function formatDateTime(date) {
    return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(new Date(date));
}

export function formatRelativeTime(date) {
    const now = new Date();
    const then = new Date(date);
    const diff = now - then;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days} روز پیش`;
    if (hours > 0) return `${hours} ساعت پیش`;
    if (minutes > 0) return `${minutes} دقیقه پیش`;
    return 'همین الان';
}

