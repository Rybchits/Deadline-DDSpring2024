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


START = range(1)

async def start_get_tasks_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.chat_id

    query = """
        SELECT t.* FROM 
            (
                SELECT Tasks.title, Tasks.start, Tasks.finish, Tasks.id
                    FROM Tasks
                    JOIN UsersTasks
                        ON Tasks.id = UsersTasks.taskId
                    WHERE UsersTasks.userId = %s
                UNION
                SELECT Tasks.title, Tasks.start, Tasks.finish, Tasks.id
                    FROM TagsTasks
                    JOIN UsersTags
                        ON TagsTasks.tagid = UsersTags.tagid
                    JOIN Tasks
                        ON Tasks.id = TagsTasks.taskid
                WHERE UsersTags.userid = %s
            ) t
            LEFT JOIN UsersTasks ON UsersTasks.taskId = t.id
            WHERE UsersTasks.done != True
            ORDER BY t.finish;
    """
    tasks = await async_sql(query, (user_id, user_id))

    if not tasks:
        await update.message.reply_text("У вас нет активных задач.")
        return ConversationHandler.END

    result = "Список ваших задач:\n"
    for id, task in enumerate(tasks):
        result += (
            f'\n{id + 1}. Задача #{task[3]} {task[0]}\n'
            f'Начало: {task[1].astimezone().strftime('%d/%m/%Y, %H:%M')}\n'
            f'Конец: {task[2].astimezone().strftime('%d/%m/%Y, %H:%M')}\n'
        )
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
