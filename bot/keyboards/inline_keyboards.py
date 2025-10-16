from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List

from core.translator import _
from database.models.plan import PlanCategory, Plan
from database.models.service import Service

def get_wallet_menu_keyboard() -> InlineKeyboardMarkup:
    """Creates the inline keyboard for the wallet menu."""
    keyboard = [
        [
            InlineKeyboardButton(_('buttons.wallet.increase_balance'), callback_data='increase_balance'),
            InlineKeyboardButton(_('buttons.wallet.transaction_history'), callback_data='transaction_history')
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_methods_keyboard(purchase_flow: bool = False) -> InlineKeyboardMarkup:
    """Creates the inline keyboard for choosing a payment method."""
    back_callback = 'back_to_plans' if purchase_flow else 'back_to_wallet'
    
    keyboard = []
    # Only show wallet payment if it's part of a purchase flow
    if purchase_flow:
        keyboard.append([InlineKeyboardButton(_('buttons.payment.wallet'), callback_data='pay_wallet')])
        
    keyboard.extend([
        [InlineKeyboardButton(_('buttons.payment.online'), callback_data='pay_online')],
        [InlineKeyboardButton(_('buttons.payment.card_to_card'), callback_data='pay_card_to_card')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data=back_callback)]
    ])

    return InlineKeyboardMarkup(keyboard)

def get_online_payment_keyboard(payment_url: str, transaction_id: int) -> InlineKeyboardMarkup:
    """Creates the keyboard with the payment link and verification button."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.payment.go_to_gateway'), url=payment_url)],
        [InlineKeyboardButton(_('buttons.payment.verify_payment'), callback_data=f'verify_payment_{transaction_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_receipt_confirmation_keyboard(transaction_id: int) -> InlineKeyboardMarkup:
    """Creates the inline keyboard for admin to confirm or reject a receipt."""
    keyboard = [
        [
            InlineKeyboardButton(_('buttons.admin.confirm_receipt'), callback_data=f'confirm_receipt_{transaction_id}'),
            InlineKeyboardButton(_('buttons.admin.reject_receipt'), callback_data=f'reject_receipt_{transaction_id}')
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_plan_categories_keyboard() -> InlineKeyboardMarkup:
    """Creates the inline keyboard for plan categories."""
    keyboard = [
        [InlineKeyboardButton(_(f'plan_categories.{cat.name}'), callback_data=f'category_{cat.name}')]
        for cat in PlanCategory
    ]
    keyboard.append([InlineKeyboardButton(_('buttons.general.cancel'), callback_data='cancel_purchase')])
    return InlineKeyboardMarkup(keyboard)

def get_plans_keyboard(plans: List[Plan]) -> InlineKeyboardMarkup:
    """Creates an inline keyboard listing available plans."""
    keyboard = []
    for plan in plans:
        button_text = _('buttons.plan_selection', name=plan.name, price=plan.price)
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'plan_{plan.id}')])
    keyboard.append([InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_categories')])
    return InlineKeyboardMarkup(keyboard)

def get_purchase_confirmation_keyboard(plan_id: int) -> InlineKeyboardMarkup:
    """Creates the confirmation keyboard for a purchase."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.purchase.confirm_buy'), callback_data=f'confirm_purchase_{plan_id}')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_plans')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_services_keyboard(services: List[Service]) -> InlineKeyboardMarkup:
    """Creates an inline keyboard listing a user's active services."""
    keyboard = []
    for service in services:
        button_text = service.note or f"{_('words.service')} #{service.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'manage_service_{service.id}')])
    return InlineKeyboardMarkup(keyboard)

def get_service_management_keyboard(service_id: int) -> InlineKeyboardMarkup:
    """Creates the detailed management menu for a specific service with better organization."""
    keyboard = [
        # دسترسی و اتصال
        [InlineKeyboardButton(_('buttons.service_manage.access_section'), callback_data=f'section_access_{service_id}')],
        # مدیریت و تنظیمات
        [InlineKeyboardButton(_('buttons.service_manage.management_section'), callback_data=f'section_manage_{service_id}')],
        # اطلاعات و پشتیبانی
        [InlineKeyboardButton(_('buttons.service_manage.info_section'), callback_data=f'section_info_{service_id}')],
        # لغو سرویس
        [InlineKeyboardButton(_('buttons.service_manage.cancel_service'), callback_data=f'cancel_service_{service_id}')],
        [InlineKeyboardButton(_('buttons.general.back_to_main_menu'), callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_service_access_section_keyboard(service_id: int) -> InlineKeyboardMarkup:
    """Keyboard for access and connection section."""
    keyboard = [
        [
            InlineKeyboardButton(_('buttons.service_manage.get_subscription'), callback_data=f'get_sub_{service_id}'),
            InlineKeyboardButton(_('buttons.service_manage.get_qr_code'), callback_data=f'get_qr_{service_id}')
        ],
        [
            InlineKeyboardButton(_('buttons.service_manage.regenerate_uuid'), callback_data=f'regen_uuid_{service_id}'),
            InlineKeyboardButton(_('buttons.service_manage.update_servers'), callback_data=f'update_servers_{service_id}')
        ],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data=f'manage_service_{service_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_service_management_section_keyboard(service_id: int) -> InlineKeyboardMarkup:
    """Keyboard for management and settings section."""
    keyboard = [
        [
            InlineKeyboardButton(_('buttons.service_manage.renew_service'), callback_data=f'renew_{service_id}'),
            InlineKeyboardButton(_('buttons.service_manage.auto_renew'), callback_data=f'toggle_renew_{service_id}')
        ],
        [
            InlineKeyboardButton(_('buttons.service_manage.change_note'), callback_data=f'edit_note_{service_id}'),
            InlineKeyboardButton(_('buttons.service_manage.connection_alerts'), callback_data=f'toggle_alerts_{service_id}')
        ],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data=f'manage_service_{service_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_service_info_section_keyboard(service_id: int) -> InlineKeyboardMarkup:
    """Keyboard for information and support section."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.service_manage.active_connections'), callback_data=f'get_connections_{service_id}')],
        [InlineKeyboardButton(_('buttons.service_manage.faq'), callback_data=f'faq_generic')],
        [InlineKeyboardButton(_('buttons.service_manage.support'), url=f"https://t.me/{_('config.support_id')}")],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data=f'manage_service_{service_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_management_keyboard(user_id: int, is_blocked: bool = False) -> InlineKeyboardMarkup:
    """Creates the management menu for a specific user in the admin panel."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.admin_user_manage.view_services'), callback_data=f'admin_view_services_{user_id}')],
        [InlineKeyboardButton(_('buttons.admin_user_manage.add_balance'), callback_data=f'admin_add_balance_{user_id}')],
        [InlineKeyboardButton(_('buttons.admin_user_manage.change_role'), callback_data=f'admin_change_role_{user_id}')],
    ]
    
    # Add block/unblock button based on current status
    if is_blocked:
        keyboard.append([InlineKeyboardButton(_('buttons.admin_user_manage.unblock_user'), callback_data=f'admin_unblock_user_{user_id}')])
    else:
        keyboard.append([InlineKeyboardButton(_('buttons.admin_user_manage.block_user'), callback_data=f'admin_block_user_{user_id}')])
    
    return InlineKeyboardMarkup(keyboard)