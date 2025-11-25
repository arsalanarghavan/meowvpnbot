# 🔧 Fix Redirect Loop

## مشکل:
`ERR_TOO_MANY_REDIRECTS` برای `/setup/welcome` و `/login`

## راه حل سریع:

```bash
# 1. بررسی Nginx config
sudo cat /etc/nginx/sites-enabled/*panel* | grep -E "return|rewrite"

# 2. اگر redirect اضافی دیدی، حذفش کن
# معمولاً مشکل از این خط است:
# return 301 https://$host$request_uri;

# 3. پاک کردن cache Laravel
cd /var/www/meowvpnbot/site
php artisan optimize:clear

# 4. ریستارت
sudo systemctl restart php8.2-fpm nginx
```

## بررسی مشکل:

```bash
# تست مستقیم Laravel (بدون Nginx)
cd /var/www/meowvpnbot/site
php artisan serve --host=127.0.0.1 --port=8000

# در ترمینال دیگه:
curl -I http://127.0.0.1:8000/setup/welcome
```

اگر این کار کرد، مشکل از Nginx است.

## اگر مشکل از Cloudflare است:

1. برو به Cloudflare Dashboard
2. SSL/TLS → Always Use HTTPS: OFF
3. یا Page Rules → Disable SSL redirect

