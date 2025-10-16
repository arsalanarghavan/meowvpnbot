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

def get_marketer_main_menu() -> ReplyKeyboardMarkup:
    """Creates the main reply keyboard for the marketer."""
    keyboard = [
        [_('buttons.main_menu.purchase_service'), _('buttons.main_menu.manage_service')],
        [_('buttons.main_menu.wallet'), _('buttons.main_menu.gift_card')],
        [_('buttons.main_menu.applications'), _('buttons.main_menu.earn_money')],
        [_('buttons.main_menu.test_account'), _('buttons.main_menu.support')],
        [_('buttons.main_menu.account_info'), _('buttons.main_menu.marketer_panel')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_marketer_panel_menu() -> ReplyKeyboardMarkup:
    """Creates the reply keyboard for the marketer panel."""
    keyboard = [
        [_('buttons.marketer_panel.invite_link'), _('buttons.marketer_panel.stats')],
        [_('buttons.marketer_panel.request_payout')],
        [_('buttons.marketer_panel.back_to_main')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_main_menu() -> ReplyKeyboardMarkup:
    """Creates the main reply keyboard for the admin panel."""
    keyboard = [
        [_('buttons.admin_panel.dashboard'), _('buttons.admin_panel.user_management')],
        [_('buttons.admin_panel.broadcast'), _('buttons.admin_panel.settings')],
        [_('buttons.admin_panel.confirm_receipts'), _('buttons.admin_panel.marketer_management')],
        [_('buttons.admin_panel.backup'), _('buttons.admin_panel.exit')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_settings_menu() -> ReplyKeyboardMarkup:
    """Creates the reply keyboard for the admin settings."""
    keyboard = [
        [_('buttons.admin_settings.edit_texts'), _('buttons.admin_settings.payment_settings')],
        [_('buttons.admin_settings.plan_management'), _('buttons.admin_settings.panel_management')],
        [_('buttons.admin_settings.card_management'), _('buttons.admin_settings.commission_settings')],
        [_('buttons.admin_settings.general_settings'), _('buttons.admin_panel.back_to_main')]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)