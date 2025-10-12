import os
import asyncio
from telegram import Update, InputFile
from telegram.ext import ContextTypes

from core.translator import _
from core.config import DATABASE_URL

async def backup_database(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the backup database command for the admin, supporting SQLite and PostgreSQL."""
    await update.message.reply_text(_('messages.backup_creating'))

    try:
        # --- SQLite Backup ---
        if DATABASE_URL.startswith("sqlite:///"):
            db_path = DATABASE_URL.split("sqlite:///")[1]
            if not os.path.exists(db_path):
                await update.message.reply_text(_('messages.backup_db_not_found'))
                return

            with open(db_path, 'rb') as db_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=InputFile(db_file, filename=f"backup_{os.path.basename(db_path)}"),
                    caption=_('messages.backup_file_caption')
                )

        # --- PostgreSQL Backup ---
        elif DATABASE_URL.startswith("postgresql://"):
            backup_file_path = "db_backup.sql"
            # Construct the pg_dump command from the DATABASE_URL
            # Example format: postgresql://user:password@host:port/dbname
            parts = DATABASE_URL.split('@')
            user_pass = parts[0].split('://')[1]
            host_db = parts[1]
            user = user_pass.split(':')[0]
            password = user_pass.split(':')[1]
            host = host_db.split(':')[0]
            port = host_db.split('/')[0].split(':')[1] if ':' in host_db.split('/')[0] else '5432'
            dbname = host_db.split('/')[1]

            # Set the password environment variable for pg_dump
            env = os.environ.copy()
            env['PGPASSWORD'] = password

            command = [
                'pg_dump',
                '--host', host,
                '--port', port,
                '--username', user,
                '--dbname', dbname,
                '--file', backup_file_path,
                '--format=c' # custom format, compressed and suitable for pg_restore
            ]

            # Execute the command
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                error_message = stderr.decode().strip()
                await update.message.reply_text(_('messages.error_general_with_details', error=error_message))
                print(f"pg_dump failed: {error_message}")
                return

            # Send the backup file
            with open(backup_file_path, 'rb') as backup_file:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=InputFile(backup_file, filename="postgresql_backup.sqlc"),
                    caption=_('messages.backup_file_caption')
                )
            # Clean up the backup file
            os.remove(backup_file_path)

        else:
            await update.message.reply_text(_('messages.backup_not_supported'))

    except Exception as e:
        await update.message.reply_text(_('messages.error_general_with_details', error=str(e)))
        print(f"Backup failed: {e}")