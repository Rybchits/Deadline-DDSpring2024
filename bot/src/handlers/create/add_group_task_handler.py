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


START, ADD_GROUP_ID, ADD_TASK_ID = range(3)

async def start_add_group_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите group id:")

    return ADD_GROUP_ID

async def add_group_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["GROUP_ID"] = update.message.text
    await update.message.reply_text("Введите task id:")

    return ADD_TASK_ID

async def add_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text
    group_id = context.user_data["GROUP_ID"]

    query = "INSERT INTO GroupsTasks(groupId, taskId) values (%s, %s);"
    run_sql(query, (group_id, task_id))

    await group_task_notifier(
        task_id,
        group_id,
        'Новый дедлайн #{task_id} {task_title} '
        'в группе #{group_id} {group_title}: {date}',
    )

    return ConversationHandler.END

def add_group_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_group_task", start_add_group_task_callback)],
        states={
            ADD_GROUP_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_group_id_callback)
            ],
            ADD_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_group_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
