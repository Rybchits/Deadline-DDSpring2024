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

    query = "SELECT Tasks.title, Tasks.start, Tasks.finish FROM Tasks JOIN UsersTasks ON Tasks.id = UsersTasks.taskId WHERE UsersTasks.userId=%s UNION (select Tasks.title, Tasks.start, Tasks.finish from tagstasks join userstags on tagstasks.tagid=userstags.tagid join tasks on tasks.id=tagstasks.taskid where userstags.userid=%s);"
    tasks = run_sql(query, (user_id, user_id))

    if not tasks:
        await update.message.reply_text("У вас нет активных задач.")
        return ConversationHandler.END

    result = "Список ваших задач:"
    for id, task in enumerate(tasks):
        result += f'\n{id + 1}. Задача {task[0]}. Началась {task[1]}. Дедлайн {task[2]}\n'

    await update.message.reply_text(result)

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
