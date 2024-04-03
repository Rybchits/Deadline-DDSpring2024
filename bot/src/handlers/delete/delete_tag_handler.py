from datetime import datetime
import asyncio
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from src.handlers.handlers import cancel_callback
from src.db.connection import conn
from src.db.helpers import run_sql

START, DELETE_TAG_TITLE = range(2)

async def start_delete_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.chat_id)

    query = "SELECT role from Users WHERE userId=%s;"
    result = run_sql(query, (user_id,))

    if not result or result[0][0] != 'admin':
        await update.message.reply_text("Вы не можете удалять тэги.")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите id тэга:")

    return DELETE_TAG_TITLE

async def delete_tag_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    id = update.message.text

    query = "DELETE FROM TAGS WHERE id=%s;"
    run_sql(query, (id))

    return ConversationHandler.END

def delete_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_tag", start_delete_tag_callback)],
        states={
            DELETE_TAG_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_tag_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
