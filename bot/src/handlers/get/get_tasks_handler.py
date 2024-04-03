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


START = range(1)

async def start_get_tasks_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.chat_id

    query = "SELECT * FROM Tasks JOIN UsersTasks ON Tasks.id = UsersTasks.taskId WHERE UsersTasks.userId=%s;"
    tasks = run_sql(query, (user_id,))

    await update.message.reply_text(str(tasks))

    return ConversationHandler.END

def get_tasks_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("get_tasks", start_get_tasks_callback)],
        states={
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_get_tasks_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
