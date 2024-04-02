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

START, ADD_USER_ID, ADD_TASK_ID = range(3)

async def start_add_user_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите user id:")

    return ADD_USER_ID

async def add_user_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["USER_ID"] = update.message.text
    await update.message.reply_text("Введите task id:")

    return ADD_TASK_ID

async def add_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text
    user_id = context.user_data["USER_ID"]

    query = "INSERT INTO UsersTasks(userId, taskId) values (%s, %s);"
    run_sql(query, (user_id, task_id))

    return ConversationHandler.END

def add_user_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_user_task", start_add_user_task_callback)],
        states={
            ADD_USER_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_user_id_callback)
            ],
            ADD_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_user_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )