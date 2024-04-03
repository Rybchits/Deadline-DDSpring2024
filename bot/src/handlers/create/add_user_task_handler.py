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

START, ADD_TASK_ID = range(2)

async def start_add_user_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название задачи:")

    return ADD_TASK_ID

async def add_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_name = update.message.text
    user_id = update.message.chat_id

    query = "SELECT id from Tasks WHERE title=%s;"
    result = run_sql(query, (task_name,))

    if not result:
        await update.message.reply_text("Введенная задача не существует.")
        return ConversationHandler.END

    task_id = result[0][0]

    query = "INSERT INTO UsersTasks(userId, taskId) values (%s, %s);"
    run_sql(query, (user_id, task_id))

    await update.message.reply_text(f'Вы успешно подписались на задачу {task_name}!')

    return ConversationHandler.END

def add_user_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("task_subscribe", start_add_user_task_callback)],
        states={
            ADD_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_user_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
