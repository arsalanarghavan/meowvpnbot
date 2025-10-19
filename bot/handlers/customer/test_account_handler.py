from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from core.config import ADMIN_IDS
from core.logger import get_logger

logger = get_logger(__name__)
from database.engine import SessionLocal
from database.queries import user_queries, plan_queries, setting_queries, panel_queries
from services.panel_api_factory import get_panel_api
from services.marzban_api import MarzbanAPI
from database.models.panel import Panel

async def get_test_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the 'Test Account' button."""
    user = update.effective_user
    db = SessionLocal()
    try:
        # Check if the feature is enabled by admin
        is_enabled = setting_queries.get_setting(db, 'test_account_enabled', 'True') == 'True'
        if not is_enabled:
            await update.message.reply_text(_('messages.test_account_disabled_by_admin'))
            return

        db_user = user_queries.find_or_create_user(db, user_id=user.id)

        if db_user.received_test_account:
            await update.message.reply_text(_('messages.test_account_already_received'))
            return

        test_plan = plan_queries.get_test_plan(db)
        if not test_plan:
            # Inform the user
            await update.message.reply_text(_('messages.test_account_not_configured'))
            # Notify all admins that the test plan is not configured
            for admin_id in ADMIN_IDS:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=_('messages.admin_test_plan_not_set_error')
                    )
                except Exception:
                    continue
            return

        await update.message.reply_text(_('messages.creating_test_account'))

        # --- Multi-panel Logic for Test Account ---
        panels = db.query(Panel).filter(Panel.is_active == True).all()
        if not panels:
            await update.message.reply_text(_('messages.no_panels_configured'))
            return

        service_username = f"test-{user.id}"
        user_details_list = []

        for panel in panels:
            try:
                api = get_panel_api(panel)
                # Use a unique username for test accounts to avoid collision
                user_details = await api.create_user(plan=test_plan, username=service_username)
                user_details_list.append(user_details)
            except Exception as e:
                logger.error(f"Error creating test account on panel {panel.name}: {e}")
                continue # Try next panel

        if not user_details_list:
            await update.message.reply_text(_('messages.error_all_panels_failed'))
            return

        # Mark the user as having received the test account
        user_queries.set_user_received_test_account(db, user_id=user.id)

        sub_link = await MarzbanAPI.get_combined_subscription_link(user_details_list)
        await update.message.reply_text(_('messages.test_account_created', sub_link=sub_link))

    except Exception as e:
        await update.message.reply_text(_('messages.error_general'))
        logger.error(f"Error creating test account: {e}")

    finally:
        db.close()