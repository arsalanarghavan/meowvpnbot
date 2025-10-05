import os
from telegram import Update, InputFile
from telegram.ext import ContextTypes

from core.translator import _
from core.config import DATABASE_URL

async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the backup database command for the admin."""
    
    # This feature is designed primarily for SQLite databases for simplicity.
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.split("sqlite:///")[1]
        
        if os.path.exists(db_path):
            try:
                await update.message.reply_text(_('messages.backup_creating'))
                
                with open(db_path, 'rb') as db_file:
                    await context.bot.send_document(
                        chat_id=update.effective_chat.id,
                        document=InputFile(db_file, filename=f"backup_{os.path.basename(db_path)}"),
                        caption=_('messages.backup_file_caption')
                    )
            except Exception as e:
                await update.message.reply_text(_('messages.error_general_with_details', error=str(e)))
                print(f"Backup failed: {e}")
        else:
            await update.message.reply_text(_('messages.backup_db_not_found'))
            
    else:
        # For other database types like PostgreSQL, a simple file send is not enough.
        # It would require command-line tools like pg_dump.
        await update.message.reply_text(_('messages.backup_not_supported'))