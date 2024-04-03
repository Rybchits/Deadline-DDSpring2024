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
from src.handlers.notify.tag_notifier import tag_task_notifier

START, DELETE_TAG_ID, DELETE_TASK_ID = range(3)


async def start_delete_tag_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите tag id:")

    return DELETE_TAG_ID

async def delete_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["TAG_ID"] = update.message.text
    await update.message.reply_text("Введите task id:")

    return DELETE_TASK_ID

async def delete_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text
    tag_id = context.user_data["TAG_ID"]

    query = "DELETE FROM TagsTasks WHERE tagId=%s AND taskId=%s;"
    run_sql(query, (tag_id, task_id))

    await tag_task_notifier(
        task_id,
        tag_id,
        'Освобождение от дедлайна #{task_id} {task_title} '
        'в тэге #{tag_id} {tag_title}: {date}',
    )

    return ConversationHandler.END

def delete_tag_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_tag_task", start_delete_tag_task_callback)],
        states={
            DELETE_TAG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_tag_id_callback)
            ],
            DELETE_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_tag_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
