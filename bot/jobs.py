import asyncio
from telegram.ext import ContextTypes
from telegram.error import Forbidden

from core.translator import _
from database.engine import SessionLocal
from database.queries import service_queries, user_queries, transaction_queries, panel_queries
from database.models.transaction import TransactionType, TransactionStatus
from services.panel_api_factory import get_panel_api
from services.marzban_api import MarzbanAPI
from core.logger import get_logger
from bot.notifications import check_and_notify_expiring_services, check_and_notify_low_traffic

logger = get_logger(__name__)

async def check_and_renew_services(context: ContextTypes.DEFAULT_TYPE):
    """
    A job that runs periodically to check for services that need auto-renewal.
    """
    logger.info("Running auto-renewal job...")
    db = SessionLocal()
    try:
        expiring_services = service_queries.get_expiring_services_with_auto_renew(db)
        if not expiring_services:
            logger.info("No services to auto-renew.")
            return

        panels = panel_queries.get_all_panels(db)
        if not panels:
            logger.warning("Auto-renewal job cannot run because no panels are configured.")
            return

        for service in expiring_services:
            user = service.user
            plan = service.plan

            # 1. Check user's wallet balance
            if user.wallet_balance < plan.price:
                logger.info(f"User {user.user_id} has insufficient balance for auto-renewal of service {service.id}.")
                try:
                    await context.bot.send_message(
                        chat_id=user.user_id,
                        text=_('messages.auto_renew_failed_balance', plan_name=plan.name, price=plan.price, balance=user.wallet_balance)
                    )
                except Forbidden:
                    logger.warning(f"User {user.user_id} has blocked the bot. Cannot send auto-renew failure message.")
                continue

            # 2. Renew on all VPN panels (Marzban/Hiddify)
            logger.info(f"Attempting to auto-renew service {service.id} for user {user.user_id}.")
            success_count = 0
            for panel in panels:
                try:
                    api = get_panel_api(panel)
                    await api.renew_user(service)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to renew user {service.username_in_panel} on panel {panel.name}: {e}")
            
            if success_count == 0:
                logger.error(f"Failed to renew service {service.id} on ALL panels. Aborting renewal.")
                continue

            # 3. Update database records
            user_queries.update_wallet_balance(db, user.user_id, -plan.price)
            tx = transaction_queries.create_transaction(db, user.user_id, plan.price, TransactionType.SERVICE_PURCHASE, plan.id)
            transaction_queries.update_transaction_status(db, tx.id, TransactionStatus.COMPLETED)
            service_queries.renew_service_record(db, service)

            logger.info(f"Successfully auto-renewed service {service.id} for user {user.user_id}.")

            # 4. Notify the user
            try:
                await context.bot.send_message(
                    chat_id=user.user_id,
                    text=_('messages.auto_renew_successful', plan_name=plan.name)
                )
            except Forbidden:
                logger.warning(f"User {user.user_id} has blocked the bot. Cannot send auto-renew success message.")
            
            await asyncio.sleep(0.1) # Avoid rate limiting

    except Exception as e:
        logger.error(f"An error occurred in the auto-renewal job: {e}", exc_info=True)
    finally:
        db.close()

async def check_services_for_notifications(context: ContextTypes.DEFAULT_TYPE):
    """Job to check services and send notifications about expiry and low traffic."""
    logger.info("Running service notification check job...")
    try:
        # Check for expiring services
        await check_and_notify_expiring_services(context.bot)
        
        # Check for services with low traffic
        await check_and_notify_low_traffic(context.bot)
        
        logger.info("Service notification check completed.")
    except Exception as e:
        logger.error(f"An error occurred in the notification job: {e}", exc_info=True)

async def reset_card_daily_amounts(context: ContextTypes.DEFAULT_TYPE):
    """Job to reset daily amounts for all card accounts at midnight."""
    from database.models.queries import card_queries
    
    logger.info("Running card accounts daily reset job...")
    db = SessionLocal()
    try:
        count = card_queries.reset_daily_amounts(db)
        logger.info(f"Reset daily amounts for {count} card accounts.")
    except Exception as e:
        logger.error(f"An error occurred in the card reset job: {e}", exc_info=True)
    finally:
        db.close()