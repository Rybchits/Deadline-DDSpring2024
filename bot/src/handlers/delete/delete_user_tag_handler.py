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

START, DELETE_TAG_ID = range(2)

async def start_delete_user_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["USER_ID"] = update.message.chat_id
    await update.message.reply_text("Введите название тэга: 🏷️")

    return DELETE_TAG_ID

async def delete_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_name = update.message.text
    user_id = context.user_data["USER_ID"]

    query = "SELECT id FROM Tags WHERE title=%s"
    result = run_sql(query, (tag_name,))

    if not result:
        await update.message.reply_text("Введенный тэг не существует. 😟")
        return ConversationHandler.END

    tag_id = result[0][0]

    query = "DELETE FROM UsersTags WHERE userId=%s AND tagId=%s;"
    run_sql(query, (user_id, tag_id))

    await update.message.reply_text(f'Вы успешно отписались от тэга {tag_name}! 🥳')

    return ConversationHandler.END

def delete_user_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("tag_unsubscribe", start_delete_user_tag_callback)],
        states={
            DELETE_TAG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_tag_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_user_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )