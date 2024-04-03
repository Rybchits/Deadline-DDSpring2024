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

START, ADD_TAG_ID = range(2)


async def start_add_user_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["USER_ID"] = update.message.chat_id
    await update.message.reply_text("Введите название тэга:")

    return ADD_TAG_ID

async def add_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_name = update.message.text
    user_id = context.user_data["USER_ID"]

    query = "SELECT id from Tags WHERE title=%s;"
    result = run_sql(query, (tag_name,))

    if not result:
        await update.message.reply_text("Введенный тэг не существует.")
        return ConversationHandler.END

    tag_id = result[0][0]

    query = "INSERT INTO UsersTags(userId, tagId) values (%s, %s);"
    run_sql(query, (user_id, tag_id))

    await update.message.reply_text(f'Вы успешно подписались на тэг {tag_name}!')

    return ConversationHandler.END

def add_user_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("tag_subscribe", start_add_user_tag_callback)],
        states={
            ADD_TAG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_tag_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_user_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
