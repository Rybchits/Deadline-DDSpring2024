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
from src.handlers.notify.group_notifier import group_task_notifier

START, DELETE_GROUP_ID, DELETE_TASK_ID = range(3)


async def start_delete_group_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите group id:")

    return DELETE_GROUP_ID

async def delete_group_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["GROUP_ID"] = update.message.text
    await update.message.reply_text("Введите task id:")

    return DELETE_TASK_ID

async def delete_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text
    group_id = context.user_data["GROUP_ID"]

    query = "DELETE FROM GroupsTasks WHERE groupId=%s AND taskId=%s;"
    run_sql(query, (group_id, task_id))

    await group_task_notifier(
        task_id,
        group_id,
        'Освобождение от дедлайна #{task_id} {task_title} '
        'в группе #{group_id} {group_title}: {date}',
    )

    return ConversationHandler.END

def delete_group_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("delete_group_task", start_delete_group_task_callback)],
        states={
            DELETE_GROUP_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_group_id_callback)
            ],
            DELETE_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, delete_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_delete_group_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
