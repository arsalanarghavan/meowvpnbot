from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries
from services.marzban_api import MarzbanAPI
from bot.keyboards.reply_keyboards import get_admin_main_menu, get_customer_main_menu, get_admin_settings_menu

async def admin_panel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point for the admin panel via the /admin command."""
    text = _('messages.admin_panel_welcome')
    reply_markup = get_admin_main_menu()
    await update.message.reply_text(text, reply_markup=reply_markup)

async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gathers and displays dashboard statistics."""
    db = SessionLocal()
    api = MarzbanAPI()
    try:
        await update.message.reply_text(_('messages.fetching_dashboard'))
        
        bot_user_count = user_queries.get_total_user_count(db)
        panel_users_data = await api.get_all_users_from_panel()
        system_stats = await api.get_system_stats()
        
        panel_user_count = panel_users_data.get('total', 0)
        online_users = system_stats.get('users_online', 0)
        
        dashboard_text = _('messages.admin_dashboard',
                           bot_users=bot_user_count,
                           panel_users=panel_user_count,
                           online_users=online_users)
                           
        await update.message.reply_text(dashboard_text, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(_('messages.error_fetching_dashboard'))
        print(f"Error showing dashboard: {e}")
    finally:
        db.close()

async def show_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Displays the admin settings menu."""
    text = _('messages.admin_settings_welcome')
    reply_markup = get_admin_settings_menu()
    await update.message.reply_text(text, reply_markup=reply_markup)

async def back_to_settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Returns to the admin settings menu."""
    query = update.callback_query
    await query.answer()
    text = _('messages.admin_settings_welcome')
    reply_markup = get_admin_settings_menu()
    # Since we are coming from an inline keyboard, we need to send a new message with the reply keyboard
    await query.message.reply_text(text, reply_markup=reply_markup)
    await query.message.delete()


async def exit_admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Exits the admin panel and returns to the customer menu."""
    text = _('messages.exited_admin_panel')
    reply_markup = get_customer_main_menu()
    await update.message.reply_text(text, reply_markup=reply_markup)