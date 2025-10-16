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
    """Gathers and displays comprehensive dashboard statistics."""
    db = SessionLocal()
    try:
        await update.message.reply_text(_('messages.fetching_dashboard'))
        
        # Bot statistics
        bot_user_count = user_queries.get_total_user_count(db)
        active_services_count = user_queries.get_active_services_count(db)
        
        # User role breakdown
        customer_count = user_queries.get_user_count_by_role(db, 'customer')
        marketer_count = user_queries.get_user_count_by_role(db, 'marketer')
        
        # Financial statistics
        total_revenue = user_queries.get_total_revenue(db)
        monthly_revenue = user_queries.get_monthly_revenue(db)
        pending_commissions = user_queries.get_total_pending_commissions(db)
        
        # Service statistics by category
        from database.models.plan import PlanCategory
        category_stats = {}
        for category in PlanCategory:
            count = user_queries.get_active_services_by_category(db, category)
            category_stats[category.name] = count
        
        # Panel statistics
        panels = panel_queries.get_all_panels(db)
        total_panel_users = 0
        total_online_users = 0
        
        tasks = []
        for panel in panels:
            if panel.is_active:
                api = MarzbanAPI(panel)
                tasks.append(api.get_all_users_from_panel())
                tasks.append(api.get_system_stats())

        if tasks:
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
        
        # Build category breakdown text
        category_breakdown = "\n".join([
            f"  • {_(f'plan_categories.{cat}')}: {count}" 
            for cat, count in category_stats.items() if count > 0
        ])
                           
        dashboard_text = _('messages.admin_dashboard_enhanced',
                           bot_users=bot_user_count,
                           customer_count=customer_count,
                           marketer_count=marketer_count,
                           active_services=active_services_count,
                           category_breakdown=category_breakdown or _('words.none'),
                           total_revenue=total_revenue,
                           monthly_revenue=monthly_revenue,
                           pending_commissions=pending_commissions,
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