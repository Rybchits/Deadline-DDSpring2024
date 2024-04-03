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

START, ADD_GROUP_NAME = range(2)

async def start_add_group_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название группы:")

    return ADD_GROUP_NAME

async def add_group_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    title = update.message.text

    query = "INSERT INTO groups(title) values (%s) RETURNING id;"
    group_id = run_sql(query, (title,))[0][0]
    
    await update.message.reply_text(f'Создана группа #{group_id}')

    return ConversationHandler.END

def add_group_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_group", start_add_group_callback)],
        states={
            ADD_GROUP_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_group_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_group_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )