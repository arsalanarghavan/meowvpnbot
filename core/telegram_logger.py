import html
import json
import traceback
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from core.config import LOG_CHANNEL_ID
from core.logger import get_logger

logger = get_logger(__name__)

async def log_error(
    context: ContextTypes.DEFAULT_TYPE, 
    error: Exception, 
    custom_message: str = "An exception was raised"
) -> None:
    """
    Formats an error message and sends it to the designated log channel.
    This function is designed to be called from within an error handler or a try-except block.
    """
    if not LOG_CHANNEL_ID:
        logger.warning("LOG_CHANNEL_ID is not set. Cannot send error log to Telegram.")
        return

    logger.error(f"Exception during '{custom_message}':", exc_info=error)

    tb_list = traceback.format_exception(None, error, error.__traceback__)
    tb_string = "".join(tb_list)

    # Try to get update object from context, if available
    update = context.update
    update_str = ""
    if isinstance(update, Update):
        update_str = json.dumps(update.to_dict(), indent=2, ensure_ascii=False)

    message = (
        f"<b>🚨 Error Report 🚨</b>\n\n"
        f"<b>Action:</b> {html.escape(custom_message)}\n\n"
        f"<b>Error:</b>\n<pre>{html.escape(str(error))}</pre>\n\n"
        f"<b>Traceback:</b>\n<pre>{html.escape(tb_string)}</pre>\n\n"
    )
    
    # Add user and chat data if available
    if context.user_data:
        message += f"<b>User Data:</b>\n<pre>{html.escape(str(context.user_data))}</pre>\n\n"
    if context.chat_data:
        message += f"<b>Chat Data:</b>\n<pre>{html.escape(str(context.chat_data))}</pre>\n\n"
    if update_str:
         message += f"<b>Full Update:</b>\n<pre>{html.escape(update_str)}</pre>"


    # Split message if it's too long for Telegram
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            await context.bot.send_message(
                chat_id=LOG_CHANNEL_ID,
                text=message[x:x+4096],
                parse_mode=ParseMode.HTML
            )
    else:
        await context.bot.send_message(
            chat_id=LOG_CHANNEL_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )