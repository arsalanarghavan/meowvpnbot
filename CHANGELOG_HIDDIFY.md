# تغییرات نسخه 2.0.0 - پشتیبانی از Hiddify

## 🎉 قابلیت‌های جدید

### 1. پشتیبانی از پنل Hiddify
- اضافه شدن کلاس `HiddifyAPI` برای ارتباط با پنل Hiddify
- امکان افزودن و مدیریت پنل‌های Hiddify در کنار Marzban
- نمایش آیکون مشخص برای هر نوع پنل (🔷 Marzban / 🔶 Hiddify)

### 2. Panel API Factory
- ایجاد سیستم Factory برای انتخاب خودکار API مناسب
- مدیریت یکپارچه انواع مختلف پنل‌ها
- سازگاری کامل با کدهای موجود

### 3. بهبود مدیریت پنل‌ها
- انتخاب نوع پنل هنگام افزودن پنل جدید
- نمایش بهتر لیست پنل‌ها با آیکون‌های مشخص
- پشتیبانی از چند نوع پنل به صورت همزمان

---

## 🔧 تغییرات فنی

### مدل دیتابیس
```python
# فیلد جدید در مدل Panel
panel_type = Column(Enum(PanelType), nullable=False, default=PanelType.MARZBAN)
```

### فایل‌های جدید
- `services/hiddify_api.py` - کلاس API برای Hiddify
- `services/panel_api_factory.py` - Factory برای انتخاب API
- `alembic/versions/004_add_panel_type.py` - مایگریشن دیتابیس
- `HIDDIFY_INTEGRATION.md` - راهنمای کامل یکپارچه‌سازی

### فایل‌های بروزرسانی شده
- `database/models/panel.py` - اضافه شدن enum PanelType
- `database/models/queries/panel_queries.py` - پشتیبانی از panel_type
- `bot/handlers/admin/panel_management.py` - UI برای انتخاب نوع پنل
- `bot/states/conversation_states.py` - state جدید برای انتخاب نوع
- `locales/fa.json` - متن‌های فارسی جدید

### تمام handler های به‌روزرسانی شده:
- `bot/handlers/customer/service_management.py`
- `bot/handlers/customer/purchase_flow.py`
- `bot/handlers/customer/payment_handlers.py`
- `bot/handlers/customer/test_account_handler.py`
- `bot/handlers/admin/financial_handlers.py`
- `bot/handlers/admin/panel.py`
- `bot/jobs.py`
- `bot/notifications.py`

---

## 📋 چک‌لیست نصب

برای استفاده از این نسخه، مراحل زیر را انجام دهید:

- [ ] Pull کردن آخرین تغییرات از git
- [ ] اجرای مایگریشن دیتابیس: `alembic upgrade head`
- [ ] Restart کردن ربات
- [ ] تست افزودن پنل Hiddify از طریق ربات
- [ ] تست ایجاد سرویس جدید

---

## ⚠️ نکات مهم

### سازگاری با نسخه قبلی
- پنل‌های Marzban موجود شما بدون هیچ تغییری کار می‌کنند
- مایگریشن به طور خودکار نوع پنل‌های موجود را به `MARZBAN` تنظیم می‌کند
- نیازی به تغییر در تنظیمات فعلی نیست

### مایگریشن دیتابیس
```bash
# نصب/بروزرسانی Alembic (در صورت نیاز)
pip install alembic

# اجرای مایگریشن
alembic upgrade head
```

### لاگ‌ها
برای عیب‌یابی احتمالی:
```bash
tail -f logs/bot.log
```

---

## 🧪 تست‌ها

### تست افزودن پنل Hiddify
1. به عنوان admin وارد ربات شوید
2. تنظیمات > مدیریت پنل‌ها > افزودن پنل جدید
3. انتخاب نوع: Hiddify
4. وارد کردن اطلاعات پنل
5. بررسی موفقیت‌آمیز بودن اتصال

### تست ایجاد سرویس
1. خرید یک سرویس جدید
2. بررسی ایجاد کاربر در پنل Hiddify
3. تست لینک اشتراک

### تست ترکیب پنل‌ها
1. افزودن هم پنل Marzban و هم Hiddify
2. خرید سرویس جدید
3. بررسی ایجاد کاربر در هر دو پنل
4. تست لینک اشتراک ترکیبی

---

## 📊 API Endpoints استفاده شده

### Hiddify
| Method | Endpoint | توضیحات |
|--------|----------|---------|
| POST | `/api/v2/admin/login` | احراز هویت |
| POST | `/api/v2/admin/user/` | ایجاد کاربر |
| GET | `/api/v2/admin/user/{username}/` | دریافت اطلاعات |
| PUT | `/api/v2/admin/user/{username}/` | بروزرسانی کاربر |
| POST | `/api/v2/admin/user/{username}/reset/` | ریست UUID |
| GET | `/api/v2/admin/system/` | آمار سیستم |
| GET | `/api/v2/admin/user/` | لیست کاربران |

---

## 🐛 مشکلات شناخته شده

### محدودیت‌های احتمالی Hiddify API
- برخی نسخه‌های Hiddify ممکن است endpoint های متفاوتی داشته باشند
- در صورت مشکل، نسخه API پنل خود را بررسی کنید

### راه‌حل
- مطمئن شوید از آخرین نسخه Hiddify استفاده می‌کنید
- در صورت نیاز، `services/hiddify_api.py` را با توجه به نسخه پنل خود تنظیم کنید

---

## 🔮 برنامه‌های آینده

- [ ] افزودن پشتیبانی از پنل‌های دیگر (X-UI, 3X-UI, etc.)
- [ ] داشبورد مدیریتی برای مانیتورینگ همزمان چند پنل
- [ ] آمارگیری تفکیک شده به تفکیک نوع پنل
- [ ] Load balancing هوشمند بین پنل‌ها

---

## 💬 بازخورد و پشتیبانی

اگر:
- مشکلی پیش آمد
- پیشنهادی دارید
- باگی پیدا کردید

لطفاً یک Issue در GitHub ایجاد کنید یا با ما تماس بگیرید.

---

## 🙏 تشکر

از استفاده از این ربات متشکریم! امیدواریم این قابلیت جدید به کسب و کار شما کمک کند.

**تیم توسعه MeowVPNBot** 🐱

