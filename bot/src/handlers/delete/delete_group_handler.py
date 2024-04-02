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

START, DELETE_GROUP_TITLE = range(2)

async def start_delete_group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название группы:")

    return DELETE_GROUP_TITLE

async def delete_group_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    title = update.message.text

    query = "DELETE FROM GROUPS WHERE TITLE=%s;"
    run_sql(query, (title))
    
    return ConversationHandler.END

def delete_group_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_group", start_delete_group_callback)],
        states={
            DELETE_GROUP_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_group_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_group_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )