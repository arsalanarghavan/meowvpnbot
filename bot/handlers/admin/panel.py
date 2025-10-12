from telegram import Update
from telegram.ext import ContextTypes
import asyncio

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries, panel_queries
from services.marzban_api import MarzbanAPI
from bot.keyboards.reply_keyboards import get_admin_main_menu, get_customer_main_menu, get_admin_settings_menu
from core.telegram_logger import log_error

async def admin_panel_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Entry point for the admin panel via the /admin command."""
    text = _('messages.admin_panel_welcome')
    reply_markup = get_admin_main_menu()
    await update.message.reply_text(text, reply_markup=reply_markup)

async def show_dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Gathers and displays dashboard statistics from all active panels."""
    db = SessionLocal()
    try:
        await update.message.reply_text(_('messages.fetching_dashboard'))
        
        bot_user_count = user_queries.get_total_user_count(db)
        panels = panel_queries.get_all_panels(db)
        
        total_panel_users = 0
        total_online_users = 0
        
        tasks = []
        for panel in panels:
            if panel.is_active:
                api = MarzbanAPI(panel)
                tasks.append(api.get_all_users_from_panel())
                tasks.append(api.get_system_stats())

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        i = 0
        while i < len(results):
            users_data = results[i]
            system_stats = results[i+1]
            
            if not isinstance(users_data, Exception):
                total_panel_users += users_data.get('total', 0)
            if not isinstance(system_stats, Exception):
                total_online_users += system_stats.get('users_online', 0)
            
            i += 2
                           
        dashboard_text = _('messages.admin_dashboard',
                           bot_users=bot_user_count,
                           panel_users=total_panel_users,
                           online_users=total_online_users)
                           
        await update.message.reply_text(dashboard_text, parse_mode='Markdown')
        
    except Exception as e:
        await update.message.reply_text(_('messages.error_fetching_dashboard'))
        await log_error(context, e, "showing dashboard")
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