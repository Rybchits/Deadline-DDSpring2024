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
async def start_get_gantt_diagram_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("GET GANTT DIAGRAM")

    return ConversationHandler.END

def get_gantt_diagram_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("get_gantt_diagram", start_get_gantt_diagram_callback)],
        states={
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_get_gantt_diagram_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )