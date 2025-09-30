from telegram import ReplyKeyboardMarkup

from core.translator import _

def get_customer_main_menu() -> ReplyKeyboardMarkup:
    """Creates the main reply keyboard for the customer."""
    keyboard = [
        [_('buttons.main_menu.purchase_service'), _('buttons.main_menu.manage_service')],
        [_('buttons.main_menu.wallet'), _('buttons.main_menu.gift_card')],
        [_('buttons.main_menu.applications'), _('buttons.main_menu.earn_money')],
        [_('buttons.main_menu.test_account'), _('buttons.main_menu.support')],
        [_('buttons.main_menu.account_info')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_main_menu() -> ReplyKeyboardMarkup:
    """Creates the main reply keyboard for the admin panel."""
    keyboard = [
        [_('buttons.admin_panel.dashboard'), _('buttons.admin_panel.user_management')],
        [_('buttons.admin_panel.broadcast'), _('buttons.admin_panel.settings')],
        [_('buttons.admin_panel.confirm_receipts')],
        [_('buttons.admin_panel.exit')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)