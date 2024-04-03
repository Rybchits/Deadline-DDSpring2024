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

START, DELETE_TASK_TITLE = range(2)

async def start_delete_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.chat_id)

    query = "SELECT role from Users WHERE userId=%s;"
    result = run_sql(query, (user_id,))

    if not result or result[0][0] != 'admin':
        await update.message.reply_text("Вы не можете удалять задачи.")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите id задачи:")

    return DELETE_TASK_TITLE 

async def delete_task_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text

    query = "DELETE FROM TASKS WHERE id=%s;"
    run_sql(query, (task_id))
    
    return ConversationHandler.END

def delete_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_task", start_delete_task_callback)],
        states={
            DELETE_TASK_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_task_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )