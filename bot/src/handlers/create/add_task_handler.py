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

START, ADD_TASK_NAME, ADD_TASK_START_DATE, ADD_TASK_END_DATE = range(4)

async def start_add_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название задачи")

    return ADD_TASK_NAME

async def add_task_name_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["TITLE"] = update.message.text

    await update.message.reply_text('Введите дату начала задачи в формате dd-mm-yyyy hh:mm UTC')
    
    return ADD_TASK_START_DATE

async def add_task_start_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["START"] = update.message.text

    await update.message.reply_text('Введите дату окончания задачи в формате dd-mm-yyyy hh:mm UTC')

    return ADD_TASK_END_DATE

async def add_task_end_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["FINISH"] = update.message.text

    task = context.user_data
    query = "INSERT INTO tasks(title, start, finish) values (%s, %s, %s) RETURNING id;"
    task_id = run_sql(
        query, (task["TITLE"], task["START"], task["FINISH"])
    )[0][0]

    await update.message.reply_text(f'Создана задача #{task_id}')

    return ConversationHandler.END


def add_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_task", start_add_task_callback)],
        states={
            ADD_TASK_END_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_end_date_callback)
            ],
            ADD_TASK_START_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_start_date_callback)
            ],
            ADD_TASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_name_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
