from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.db.helpers import run_sql

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello my dear friend!")

    query = "INSERT INTO users(name, userid) values (%s, %s);"
    run_sql(query, (update.message.from_user.username, update.message.chat_id))

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END