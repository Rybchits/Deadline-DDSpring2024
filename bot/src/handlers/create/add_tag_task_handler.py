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
    filters,
    CallbackQueryHandler,
)

from src.handlers.handlers import cancel_callback
from src.db.helpers import async_sql
from src.handlers.notify.tag_notifier import tag_task_notifier

START, ADD_TAG_ID, ADD_TASK_ID = range(3)


async def start_add_tag_task_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = update.message.chat_id

    sql_query = f"""
        SELECT * from userstags 
        join tags on userstags.tagId = Tags.id
        WHERE userId={user_id} and is_admin=true;
    """
    user_tags = await async_sql(sql_query)
    if not user_tags:
        await update.message.reply_text(
            "У вас нет доступных тэгов для привязки задачи. Заведите его 🙂"
        )
        return ConversationHandler.END

    buttons = []
    for i in range(0, len(user_tags), 2):
        pair = []
        pair.append(
            InlineKeyboardButton(
                user_tags[i]["title"], callback_data=user_tags[i]["id"]
            )
        )
        if i + 1 != len(user_tags):
            pair.append(
                InlineKeyboardButton(
                    user_tags[i + 1]["title"], callback_data=user_tags[i + 1]["id"]
                )
            )
        buttons.append(pair)

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.effective_message.reply_text(
        "Укажите тэг, к которому вы хотите привязать задачу: 🏷️",
        reply_markup=reply_markup,
    )

    return ADD_TAG_ID


async def add_tag_id_callback(
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

    tag_id = int(query.data)
    context.user_data["TAG_ID"] = tag_id

    user_id = query.message.chat_id

    sql_query = f"""
        SELECT Tasks.id, Tasks.title FROM UsersTasks
            JOIN Tasks ON UsersTasks.taskId = Tasks.id and UsersTasks.userId = {user_id}
            LEFT JOIN TagsTasks ON TagsTasks.taskId = Tasks.id and TagsTasks.tagId={tag_id}
        WHERE tagstasks.tagId IS NULL;
    """
    tasks = await async_sql(sql_query)
    if not tasks:
        await query.message.reply_text(
            "У вас нет доступных для привязки задач. Заведите их 🙂"
        )
        return ConversationHandler.END

    buttons = []
    for i in range(0, len(tasks), 2):
        pair = []
        pair.append(
            InlineKeyboardButton(tasks[i]["title"], callback_data=tasks[i]["id"])
        )
        if i + 1 != len(tasks):
            pair.append(
                InlineKeyboardButton(
                    tasks[i + 1]["title"], callback_data=tasks[i + 1]["id"]
                )
            )
        buttons.append(pair)

    reply_markup = InlineKeyboardMarkup(buttons)

    await update.effective_message.reply_text(
        "Укажите задачу, которую вы хотите привязать тег: 🏷️", reply_markup=reply_markup
    )

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

    task_id = int(query.data)
    tag_id = context.user_data["TAG_ID"]

    sql_query = f"INSERT INTO TagsTasks(tagId, taskId) values ({tag_id}, {task_id});"
    await async_sql(sql_query)

    await tag_task_notifier(
        task_id,
        tag_id,
        "Новый дедлайн #{task_id} {task_title} " "в тэге #{tag_id} {tag_title}: {date}",
    )

    return ConversationHandler.END


def add_tag_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_tag_task", start_add_tag_task_callback)],
        states={
            ADD_TAG_ID: [CallbackQueryHandler(add_tag_id_callback)],
            ADD_TASK_ID: [CallbackQueryHandler(add_task_id_callback)],
            START: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, start_add_tag_task_callback
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)],
    )
