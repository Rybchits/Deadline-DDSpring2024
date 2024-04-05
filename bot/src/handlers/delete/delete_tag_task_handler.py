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
    user_id = str(update.message.chat_id)

    query = "SELECT role from Users WHERE userId=%s;"
    result = run_sql(query, (user_id,))

    if not result or result[0][0] != 'admin':
        await update.message.reply_text("Вы не достаточно всемогущ, чтобы делать это! 😟")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите название тэга: 🏷️")

    return DELETE_TAG_ID

async def delete_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_name = update.message.text
    
    query = "SELECT id from tags WHERE title=%s;"
    tag_id = run_sql(query, (tag_name,))

    context.user_data["TAG_ID"] = tag_id
    await update.message.reply_text("Введите название задачи: 📚")

    return DELETE_TASK_ID

async def delete_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.chat_id
    task_name = update.message.text
    query = "SELECT title from tasks WHERE id=%s;"
    task_id = run_sql(query, (task_name,))

    tag_id = context.user_data["TAG_ID"]

    query = "DELETE FROM TagsTasks WHERE tagId=%s AND taskId=%s;"
    run_sql(query, (tag_id, task_id))

    await tag_task_notifier(
        task_id,
        tag_id,
        user_id,
        'Освобождение от дедлайна #{task_id} {task_title} '
        'в тэге #{tag_id} {tag_title}: {date} 🥲',
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
