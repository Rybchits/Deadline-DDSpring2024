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

START, ADD_TAG_NAME = range(2)

async def start_add_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.chat_id)

    query = "SELECT role from Users WHERE userId=%s;"
    result = run_sql(query, (user_id,))

    if not result or result[0][0] != 'admin':
        await update.message.reply_text("Вы не можете добавлять новые тэги.")
        return ConversationHandler.END

    await update.message.reply_text("Введите название тэга:")

    return ADD_TAG_NAME

async def add_tag_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    title = update.message.text

    query = "INSERT INTO tags(title) values (%s) RETURNING id;"
    tag_id = run_sql(query, (title,))[0][0]
    
    await update.message.reply_text(f'Создан тэг {title}!')

    return ConversationHandler.END

def add_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_tag", start_add_tag_callback)],
        states={
            ADD_TAG_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_tag_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )