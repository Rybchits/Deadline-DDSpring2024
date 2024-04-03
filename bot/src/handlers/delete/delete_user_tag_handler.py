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

START, DELETE_USER_ID, DELETE_TAG_ID = range(3)

async def start_delete_user_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите user id:")

    return DELETE_USER_ID

async def delete_user_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["USER_ID"] = update.message.text
    await update.message.reply_text("Введите tag id:")

    return DELETE_TAG_ID

async def delete_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_id = update.message.text
    user_id = context.user_data["USER_ID"]

    query = "DELETE FROM UsersTags WHERE userId=%s AND tagId=%s;"
    run_sql(query, (user_id, tag_id))

    return ConversationHandler.END

def delete_user_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_user_tag", start_delete_user_tag_callback)],
        states={
            DELETE_USER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_user_id_callback)
            ],
            DELETE_TAG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_tag_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_user_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )