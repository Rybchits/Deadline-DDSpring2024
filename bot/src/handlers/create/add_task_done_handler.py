from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from src.handlers.handlers import cancel_callback
from src.db.helpers import async_sql

START, ADD_TASK_ID = range(2)


async def start_add_task_done_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text("Введите название задачи: 📚")

    return ADD_TASK_ID


async def add_task_id_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = update.message.chat_id
    task_name = update.message.text

    query = "SELECT id from Tasks WHERE title=$1;"
    result = await async_sql(query, (task_name,))

    if not result:
        await update.message.reply_text("Введенная задача не существует. 😟")
        return ConversationHandler.END

    task_id = result[0][0]
    query = (
        'INSERT INTO UsersTasks (userId, taskId, done) '
        'values ($1, $2, TRUE) ON CONFLICT (userId, taskId) DO '
        'UPDATE SET done = TRUE'
    )
    await async_sql(query, (user_id, task_id))

    await update.message.reply_text(f"Задача {task_name} выполнена! 🕺")

    return ConversationHandler.END


def add_task_done_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("do_task", start_add_task_done_callback)],
        states={
            ADD_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND,
                               add_task_id_callback)
            ],
            START: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    start_add_task_done_callback
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)],
    )
