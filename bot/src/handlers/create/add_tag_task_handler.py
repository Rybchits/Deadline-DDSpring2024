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
from src.db.helpers import async_sql
from src.handlers.notify.tag_notifier import tag_task_notifier


START, ADD_TAG_ID, ADD_TASK_ID = range(3)

async def start_add_tag_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите tag id:")

    return ADD_TAG_ID

async def add_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_id = update.message.text
    user_id = update.message.chat_id

    context.user_data["TAG_ID"] = tag_id

    query = f"SELECT is_admin from userstags WHERE userId={user_id} and tagId={tag_id};"
    result = await async_sql(query)
    print(result)

    if not result or not result[0][0]:
        await update.message.reply_text("Вы не можете добавлять этот дедайн в этот тег. Вы не являетесь его админом")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите task id:")

    return ADD_TASK_ID

async def add_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_id = update.message.text
    tag_id = context.user_data["TAG_ID"]

    # TODO: move into transaction

    check_task_query = f"SELECT * from tasks WHERE id={task_id};"
    result = await async_sql(check_task_query)
    print(result)

    if not result:
        await update.message.reply_text("Дедлайна с таким id нет")
        return ConversationHandler.END

    insert_query = f"INSERT INTO TagsTasks(tagId, taskId) values ({tag_id}, {task_id});"
    await async_sql(insert_query)

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
