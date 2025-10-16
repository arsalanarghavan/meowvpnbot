# 🎉 قابلیت جدید: سیستم مدیریت هوشمند چند کارت بانکی

## 🌟 خلاصه

یک سیستم پیشرفته و کاملاً خودکار برای مدیریت چند شماره کارت در پرداخت کارت به کارت!

---

## ✨ قابلیت‌ها

### 💳 مدیریت چند کارت
- اضافه کردن کارت‌های بانکی نامحدود
- ویرایش، حذف، فعال/غیرفعال کردن
- مشاهده آمار لحظه‌ای

### 📊 سقف روزانه
- تعیین حداکثر مبلغ دریافتی روزانه برای هر کارت
- نمایش دریافتی امروز
- نمایش ظرفیت باقیمانده
- درصد استفاده

### 🔢 اولویت‌بندی
- تعیین ترتیب استفاده از کارت‌ها
- عدد کوچکتر = اولویت بالاتر
- انتخاب خودکار بر اساس اولویت

### 🔄 تعویض هوشمند
- وقتی سقف یک کارت پر شد، **خودکار** به کارت بعدی می‌رود
- الگوریتم هوشمند انتخاب کارت
- Fallback به سیستم قدیمی (settings)

### 🕐 Reset خودکار
- هر شب نیمه شب (00:01)
- صفر شدن خودکار مبالغ روزانه
- آماده برای روز جدید

---

## 📁 فایل‌های ایجاد شده

### 1. Model:
```
database/models/card_account.py
```
**شامل:**
- کلاس CardAccount
- متدهای has_capacity() و remaining_capacity()

### 2. Queries:
```
database/models/queries/card_queries.py
```
**توابع:**
- `create_card_account()` - ایجاد کارت جدید
- `get_all_cards()` - لیست کارت‌ها
- `get_available_card_for_amount()` - انتخاب هوشمند کارت
- `add_amount_to_card()` - افزودن مبلغ
- `reset_daily_amounts()` - reset روزانه
- `update_card()` - به‌روزرسانی
- `delete_card()` - حذف
- `toggle_card_status()` - فعال/غیرفعال
- `get_card_statistics()` - آمار

### 3. Handler:
```
bot/handlers/admin/card_management.py
```
**Handler ها:**
- `list_card_accounts()` - نمایش لیست
- `show_card_management_menu()` - منوی مدیریت
- `start_add_card()` - شروع افزودن
- `toggle_card_status()` - تغییر وضعیت
- `delete_card_confirm()` - حذف با تایید
- Conversation handler کامل

### 4. Migration:
```
alembic/versions/003_add_card_accounts.py
```

### 5. Documentation:
```
CARD_MANAGEMENT_GUIDE.md
```
راهنمای کامل 40+ خط!

---

## 🔄 فایل‌های به‌روزرسانی شده

1. ✅ `bot/handlers/customer/payment_handlers.py`
   - انتخاب خودکار کارت
   - Fallback به سیستم قدیمی
   
2. ✅ `bot/handlers/admin/financial_handlers.py`
   - به‌روزرسانی current_amount پس از تایید رسید
   
3. ✅ `bot/jobs.py`
   - اضافه شدن `reset_card_daily_amounts()`
   
4. ✅ `main.py`
   - ثبت handler ها
   - ثبت job روزانه reset
   
5. ✅ `bot/states/conversation_states.py`
   - 8 state جدید
   
6. ✅ `bot/keyboards/reply_keyboards.py`
   - دکمه مدیریت کارت‌ها
   
7. ✅ `locales/fa.json`
   - 20+ متن فارسی جدید

---

## 💬 متن‌های فارسی جدید

### پیام‌ها:
- admin_no_cards
- admin_add_first_card
- admin_cards_list_header
- admin_card_item
- admin_card_details
- admin_enter_card_number
- admin_enter_card_holder
- admin_enter_card_limit
- admin_enter_card_priority
- admin_enter_card_note_optional
- admin_confirm_card_creation
- admin_card_created_successfully
- admin_card_updated
- admin_card_deleted
- admin_card_activated
- admin_card_deactivated
- admin_confirm_card_deletion
- admin_enter_new_card_limit
- admin_enter_new_card_priority
- admin_enter_new_card_note
- admin_no_active_card
- error_invalid_card_number
- error_invalid_card_holder

### دکمه‌ها:
- card_management (7 دکمه)

---

## 🚀 نحوه استفاده

### برای ادمین:

```
1. /admin
2. ⚙️ تنظیمات ربات
3. 💳 مدیریت کارت‌ها
4. ➕ افزودن کارت جدید
5. وارد کردن اطلاعات:
   - شماره کارت: 6037997712345678
   - نام: علی محمدی
   - سقف روزانه: 50000000 (یا 0 برای نامحدود)
   - اولویت: 0 (عدد کوچکتر = اولویت بالاتر)
   - یادداشت: کارت اصلی
6. تایید
✅ کارت اضافه شد!
```

### برای کاربر (خودکار):

```
1. خرید سرویس یا شارژ کیف پول
2. انتخاب پرداخت کارت به کارت
3. سیستم خودکار کارت مناسب را انتخاب می‌کند:
   - با بالاترین اولویت
   - که ظرفیت کافی دارد
4. شماره کارت نمایش داده می‌شود
5. کاربر واریز می‌کند
6. پس از تایید ادمین:
   - مبلغ به current_amount کارت اضافه می‌شود
```

---

## 🎯 مثال عملی

### پیکربندی:

```python
# کارت 1
card_number: "6037997712345678"
card_holder: "علی محمدی"
daily_limit: 50_000_000  # پنجاه میلیون
priority: 0
current_amount: 35_000_000  # سی و پنج میلیون دریافت شده
remaining: 15_000_000  # پانزده میلیون باقیمانده

# کارت 2
card_number: "6219991234567890"
card_holder: "رضا احمدی"  
daily_limit: 0  # نامحدود
priority: 1
current_amount: 20_000_000
remaining: ∞  # نامحدود
```

### سناریو:

```
کاربر A می‌خواهد 10 میلیون واریز کند:
→ کارت 1 ظرفیت دارد (15M باقیمانده)
→ کارت 1 انتخاب می‌شود ✅

کاربر B می‌خواهد 20 میلیون واریز کند:
→ کارت 1 ظرفیت ندارد (فقط 5M باقیمانده)
→ کارت 2 انتخاب می‌شود ✅

پس از تایید واریز کاربر A:
→ current_amount کارت 1 = 45M
→ remaining کارت 1 = 5M

پس از تایید واریز کاربر B:
→ current_amount کارت 2 = 40M
```

---

## 🎊 مزایا

### ✅ جلوگیری از مسدودسازی
بانک‌ها معمولاً کارت‌هایی را که مبلغ زیادی در یک روز دریافت می‌کنند، مسدود می‌کنند. با این سیستم:
- مبلغ بین چند کارت توزیع می‌شود
- هیچ کارتی بیش از حد مشخص پول دریافت نمی‌کند

### ✅ مدیریت آسان
- دیگر نیازی به تغییر دستی شماره کارت نیست
- سیستم خودکار کارت مناسب را انتخاب می‌کند

### ✅ افزایش ظرفیت
- با N کارت، می‌توانید N برابر بیشتر دریافت کنید
- مثال: 3 کارت با سقف 50M = 150M ظرفیت روزانه

### ✅ انعطاف‌پذیری
- تنظیمات کامل برای هر کارت
- اولویت‌بندی بر اساس نیاز
- فعال/غیرفعال موقت

---

## 🔧 تنظیمات پیشنهادی

### برای فروش روزانه تا 100 میلیون:

```
کارت 1: سقف 50M، اولویت 0
کارت 2: سقف 50M، اولویت 1
کارت پشتیبان: نامحدود، اولویت 2
```

### برای فروش روزانه تا 200 میلیون:

```
کارت 1: سقف 50M، اولویت 0
کارت 2: سقف 50M، اولویت 1  
کارت 3: سقف 50M، اولویت 2
کارت 4: سقف 50M، اولویت 3
کارت پشتیبان: نامحدود، اولویت 4
```

---

<div align="center">

## 🎉 تبریک!

**شما الان یک سیستم مدیریت کارت حرفه‌ای دارید!**

این قابلیت شما را از 99% ربات‌های VPN متمایز می‌کند! 🏆

---

**راهنمای کامل:** [CARD_MANAGEMENT_GUIDE.md](CARD_MANAGEMENT_GUIDE.md)

</div>

