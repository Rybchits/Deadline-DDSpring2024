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


START, ADD_TAG_ID, ADD_TASK_ID = range(3)

async def start_add_tag_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите tag id:")

    return ADD_TAG_ID

async def add_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = str(update.message.chat_id)

    query = "SELECT is_admin from usertags WHERE userId=%s;"
    result = run_sql(query, (user_id,))
    print(result)

    if not result or result[0][0]:
        await update.message.reply_text("Вы не можете добавлять этот дедайн в этот тег. Вы не являетесь его админом тега")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите task id:")

    return ADD_TASK_ID

async def add_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text
    tag_id = context.user_data["TAG_ID"]

    check_task_query = "SELECT * from tasks WHERE taskId=%s;"
    result = run_sql(check_task_query, (task_id,))
    print(result)

    if not result:
        await update.message.reply_text("Дедлайна с таким id нет")
        return ConversationHandler.END

    insert_query = "INSERT INTO TagsTasks(tagId, taskId) values (%s, %s);"
    run_sql(insert_query, (tag_id, task_id))

    await tag_task_notifier(
        task_id,
        tag_id,
        'Новый дедлайн #{task_id} {task_title} '
        'в тэге #{tag_id} {tag_title}: {date}',
    )

    return ConversationHandler.END

def add_tag_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_tag_task", start_add_tag_task_callback)],
        states={
            ADD_TAG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_tag_id_callback)
            ],
            ADD_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_tag_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
