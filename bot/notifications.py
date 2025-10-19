"""
Notification system for sending alerts to users about important events.
"""
from telegram import Bot
from telegram.error import TelegramError
from database.engine import SessionLocal
from database.queries import service_queries, user_queries
from core.translator import _
from core.logger import get_logger
from datetime import datetime, timedelta

logger = get_logger(__name__)

async def check_and_notify_expiring_services(bot: Bot) -> None:
    """Check for services expiring soon and notify users."""
    db = SessionLocal()
    try:
        # Get services expiring in next 3 days
        services_expiring_soon = service_queries.get_services_expiring_soon(db, days=3)
        
        for service in services_expiring_soon:
            user = service.user
            
            # Only notify if user has alerts enabled
            if not service.connection_alerts or not user.is_active:
                continue
            
            days_until_expiry = (service.expire_date - datetime.utcnow()).days
            
            try:
                await bot.send_message(
                    chat_id=user.user_id,
                    text=_('messages.service_expiring_soon',
                          note=service.note or f"{_('words.service')} #{service.id}",
                          days=days_until_expiry,
                          expire_date=service.expire_date.strftime('%Y-%m-%d'))
                )
                logger.info(f"Sent expiry notification to user {user.user_id} for service {service.id}")
            except TelegramError as e:
                logger.error(f"Failed to send expiry notification to user {user.user_id}: {e}")
                
    finally:
        db.close()

async def check_and_notify_low_traffic(bot: Bot) -> None:
    """Check for services with low remaining traffic and notify users."""
    from services.panel_api_factory import get_panel_api
    from database.queries import panel_queries
    
    db = SessionLocal()
    try:
        active_services = service_queries.get_all_active_services(db)
        panels = panel_queries.get_all_panels(db)
        
        for service in active_services:
            user = service.user
            
            # Only notify if user has alerts enabled
            if not service.connection_alerts or not user.is_active:
                continue
            
            # Check traffic on one of the panels
            for panel in panels:
                if not panel.is_active:
                    continue
                    
                try:
                    api = get_panel_api(panel)
                    panel_user = await api.get_user(service.username_in_panel)
                    
                    if not panel_user:
                        continue
                    
                    data_limit = panel_user.get('data_limit', 0)
                    used_traffic = panel_user.get('used_traffic', 0)
                    
                    # Skip unlimited plans
                    if data_limit == 0:
                        continue
                    
                    # Calculate remaining percentage
                    remaining_percentage = ((data_limit - used_traffic) / data_limit) * 100
                    
                    # Notify if less than 20% remaining
                    if remaining_percentage < 20 and remaining_percentage > 0:
                        remaining_gb = round((data_limit - used_traffic) / (1024**3), 2)
                        
                        await bot.send_message(
                            chat_id=user.user_id,
                            text=_('messages.service_low_traffic',
                                  note=service.note or f"{_('words.service')} #{service.id}",
                                  remaining_gb=remaining_gb,
                                  percentage=round(remaining_percentage, 1))
                        )
                        logger.info(f"Sent low traffic notification to user {user.user_id} for service {service.id}")
                    
                    break  # Only check one panel per service
                    
                except Exception as e:
                    logger.error(f"Error checking traffic for service {service.id}: {e}")
                    continue
                    
    finally:
        db.close()

async def notify_service_expired(bot: Bot, service_id: int) -> None:
    """Notify user that their service has expired."""
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        if not service:
            return
        
        user = service.user
        if not user.is_active:
            return
        
        try:
            await bot.send_message(
                chat_id=user.user_id,
                text=_('messages.service_expired',
                      note=service.note or f"{_('words.service')} #{service.id}")
            )
            logger.info(f"Sent expiry notification to user {user.user_id} for service {service_id}")
        except TelegramError as e:
            logger.error(f"Failed to send expiry notification to user {user.user_id}: {e}")
            
    finally:
        db.close()

async def notify_auto_renew_success(bot: Bot, user_id: int, service_id: int) -> None:
    """Notify user that their service was auto-renewed successfully."""
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        if not service:
            return
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=_('messages.auto_renew_successful',
                      plan_name=service.plan.name)
            )
        except TelegramError as e:
            logger.error(f"Failed to send auto-renew success notification: {e}")
            
    finally:
        db.close()

async def notify_auto_renew_failed(bot: Bot, user_id: int, service_id: int, reason: str = "insufficient_balance") -> None:
    """Notify user that their service auto-renewal failed."""
    db = SessionLocal()
    try:
        service = service_queries.get_service_by_id(db, service_id)
        user = user_queries.find_user_by_id(db, user_id)
        
        if not service or not user:
            return
        
        try:
            await bot.send_message(
                chat_id=user_id,
                text=_('messages.auto_renew_failed_balance',
                      plan_name=service.plan.name,
                      price=service.plan.price,
                      balance=user.wallet_balance)
            )
        except TelegramError as e:
            logger.error(f"Failed to send auto-renew failed notification: {e}")
            
    finally:
        db.close()

