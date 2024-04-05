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
from src.db.helpers import async_sql

START, DELETE_TAG_TITLE = range(2)

async def start_delete_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.chat_id)

    query = "SELECT role from Users WHERE userId=%s;"
    result = run_sql(query, (user_id,))

    if not result or result[0][0] != 'admin':
        await update.message.reply_text("Вы не достаточно всемогущ, чтобы делать это! 🤷🏼‍♂️")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите название тэга: 🏷️")

    return DELETE_TAG_TITLE

async def delete_tag_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_name = update.message.text

    query = f'SELECT id from tags where title={tag_name}'
    tag_id = await async_sql(query)

    query = "DELETE FROM TAGS WHERE id=%s;"
    run_sql(query, (tag_id))

    await update.message.reply_text(f'Тэг {tag_name} успешно удален! ✅')

    return ConversationHandler.END

def delete_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_tag", start_delete_tag_callback)],
        states={
            DELETE_TAG_TITLE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_tag_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
