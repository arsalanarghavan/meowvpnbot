from telegram import InlineKeyboardButton, InlineKeyboardMarkup

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

def get_payment_methods_keyboard() -> InlineKeyboardMarkup:
    """Creates the inline keyboard for choosing a payment method."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.payment.card_to_card'), callback_data='pay_card_to_card')],
        [InlineKeyboardButton(_('buttons.general.back'), callback_data='back_to_wallet')]
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

def get_plans_keyboard(plans: list[Plan]) -> InlineKeyboardMarkup:
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

def get_user_services_keyboard(services: list[Service]) -> InlineKeyboardMarkup:
    """Creates an inline keyboard listing a user's active services."""
    keyboard = []
    for service in services:
        button_text = service.note or f"سرویس #{service.id}"
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'manage_service_{service.id}')])
    return InlineKeyboardMarkup(keyboard)

def get_service_management_keyboard(service_id: int) -> InlineKeyboardMarkup:
    """Creates the management menu for a specific service."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.service_manage.get_subscription'), callback_data=f'get_sub_{service_id}')],
        [InlineKeyboardButton(_('buttons.service_manage.active_connections'), callback_data=f'get_connections_{service_id}')],
        [InlineKeyboardButton(_('buttons.service_manage.regenerate_uuid'), callback_data=f'regen_uuid_{service_id}')],
        [InlineKeyboardButton(_('buttons.general.back_to_main_menu'), callback_data='back_to_main_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_user_management_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Creates the management menu for a specific user in the admin panel."""
    keyboard = [
        [InlineKeyboardButton(_('buttons.admin_user_manage.view_services'), callback_data=f'admin_view_services_{user_id}')],
        [InlineKeyboardButton(_('buttons.admin_user_manage.add_balance'), callback_data=f'admin_add_balance_{user_id}')],
        # [InlineKeyboardButton(_('buttons.admin_user_manage.ban_user'), callback_data=f'admin_ban_{user_id}')]
    ]
    return InlineKeyboardMarkup(keyboard)