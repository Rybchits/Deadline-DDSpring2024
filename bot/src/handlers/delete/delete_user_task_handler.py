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

START, DELETE_TASK_ID = range(2)

async def start_delete_user_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название задачи:")
    context.user_data["USER_ID"] = update.message.chat_id

    return DELETE_TASK_ID

async def delete_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_name = update.message.text
    user_id = context.user_data["USER_ID"]

    query = "SELECT id FROM Tasks WHERE title=%s"
    result = run_sql(query, (task_name,))

    if not result:
        await update.message.reply_text("Введенная задача не существует.")
        return ConversationHandler.END

    task_id = result[0][0]

    query = "DELETE FROM UsersTasks WHERE userId=%s AND taskId=%s;"
    run_sql(query, (user_id, task_id))

    await update.message.reply_text(f'Вы успешно отписались от задачи {task_name}!')

    return ConversationHandler.END

def delete_user_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("task_unsubscribe", start_delete_user_task_callback)],
        states={
            DELETE_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_user_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )