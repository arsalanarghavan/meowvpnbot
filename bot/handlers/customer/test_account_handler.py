from telegram import Update
from telegram.ext import ContextTypes

from core.translator import _
from database.engine import SessionLocal
from database.queries import user_queries, plan_queries
from services.marzban_api import MarzbanAPI

async def get_test_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler for the 'Test Account' button."""
    user = update.effective_user
    db = SessionLocal()
    try:
        db_user = user_queries.find_or_create_user(db, user_id=user.id)
        
        if db_user.received_test_account:
            await update.message.reply_text(_('messages.test_account_already_received'))
            return

        test_plan = plan_queries.get_test_plan(db)
        if not test_plan:
            await update.message.reply_text(_('messages.test_account_not_configured'))
            return
            
        await update.message.reply_text(_('messages.creating_test_account'))

        # --- API Call ---
        marzban_api = MarzbanAPI()
        try:
            marzban_user = await marzban_api.create_user(plan=test_plan, user_id=user.id)
            
            # Mark the user as having received the test account
            user_queries.set_user_received_test_account(db, user_id=user.id)
            
            sub_link = marzban_user.get('subscription_url', 'Not found')
            await update.message.reply_text(_('messages.test_account_created', sub_link=sub_link))

        except Exception as e:
            await update.message.reply_text(_('messages.error_general'))
            print(f"Error creating test account: {e}")

    finally:
        db.close()