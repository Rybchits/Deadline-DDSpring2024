from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Hello my dear friend!")

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END