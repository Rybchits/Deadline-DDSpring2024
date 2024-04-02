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

START = range(1)
async def start_add_user_group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("ADD USER GROUP")

    return ConversationHandler.END

def add_user_group_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_user_group", start_add_user_group_callback)],
        states={
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_user_group_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )