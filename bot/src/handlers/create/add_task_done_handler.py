from telegram import (
    Update,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)

from src.handlers.handlers import cancel_callback
from src.db.helpers import run_sql, async_sql

START, ADD_TASK_ID = range(2)


async def start_add_task_done_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
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

    tasks = run_sql(query, (user_id, user_id))

    if not tasks:
        await update.message.reply_text("У вас нет невыполненных задач 🕺")
        return ConversationHandler.END

    buttons = []
    for i in range(0, len(tasks), 2):
        pair = []
        pair.append(InlineKeyboardButton(tasks[i][0], callback_data=tasks[i][0]))
        if (i + 1 != len(tasks)):
            pair.append(InlineKeyboardButton(tasks[i + 1][0], callback_data=tasks[i + 1][0]))
        buttons.append(pair)
    
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.effective_message.reply_text("Выберите название задачи: 📚", reply_markup=reply_markup)

    return ADD_TASK_ID


async def add_task_id_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    query = update.callback_query

    await context.bot.edit_message_text(
        text=query.message.text,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )

    await context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=query.data,
        reply_markup=ReplyKeyboardRemove(),
    )

    user_id = query.message.chat.id
    task_name = str(query.data)

    query = "SELECT id from Tasks WHERE title=$1;"
    result = await async_sql(query, (task_name,))

    task_id = result[0][0]
    query = (
        'INSERT INTO UsersTasks (userId, taskId, done) '
        'values ($1, $2, TRUE) ON CONFLICT (userId, taskId) DO '
        'UPDATE SET done = TRUE'
    )
    await async_sql(query, (user_id, task_id))

    await update.effective_message.reply_text(f"Задача {task_id} выполнена! 🕺")

    return ConversationHandler.END


def add_task_done_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("do_task", start_add_task_done_callback)],
        states={
            ADD_TASK_ID: [CallbackQueryHandler(add_task_id_callback)],
            START: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    start_add_task_done_callback
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)],
    )
