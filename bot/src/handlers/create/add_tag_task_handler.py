from datetime import datetime
import asyncio
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
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
    user_id = update.message.chat_id
    
    query = f"""
        SELECT * from userstags 
        join tags on userstags.tagId = Tags.id
        WHERE userId={user_id} and is_admin=true;
    """
    user_tags = await async_sql(query)

    if not user_tags:
        await update.message.reply_text("У вас нет доступных тэгов для привязки задачи. Заведите его 🙂")
        return ConversationHandler.END

    buttons = []
    for i in range(0, len(user_tags), 2):
        pair = []
        pair.append(InlineKeyboardButton(user_tags[i]['title'], callback_data=user_tags[i]["id"]))
        if (i + 1 != len(user_tags)):
            pair.append(InlineKeyboardButton(user_tags[i + 1]['title'], callback_data=user_tags[i + 1]["id"]))
        buttons.append(pair)
    
    reply_markup = InlineKeyboardMarkup(buttons)

    await update.message.reply_text("Выберите предмет", reply_markup=reply_markup)
    await update.message.reply_text("Укажите тэг, к которому вы хотите привязать задачу: 🏷️", reply_markup=reply_markup)

    return ADD_TAG_ID

async def add_tag_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    tag_name = update.message.text
    user_id = update.message.chat_id

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

    # query = f'SELECT id from TAGS where title={tag_name};'
    # tag_id = await async_sql(query)
    # tag_id = tag_id[0]["id"]

    tag_id = int(query.data)
    context.user_data["TAG_ID"] = tag_id

    query = f"SELECT is_admin from userstags WHERE userId={user_id} and tagId={tag_id};"
    result = await async_sql(query)

    if not result or not result[0]["is_admin"]:
        await update.message.reply_text("Вы не можете добавить задачу в этот тег. Вы не являетесь его админом 😟")
        return ConversationHandler.END
    
    await update.message.reply_text("Введите название задачи: 📚")

    return ADD_TASK_ID

async def add_task_id_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    task_name = update.message.text
    tag_id = context.user_data["TAG_ID"]

    # TODO: move into transaction

    query = f"SELECT id from tasks WHERE title={task_name};"
    task_id = await async_sql(query)

    check_task_query = f"SELECT * from tasks WHERE id={task_id};"
    result = await async_sql(check_task_query)

    if not result:
        await update.message.reply_text(f'Задачи {task_name} не существует 🥲')
        return ConversationHandler.END

    insert_query = f"INSERT INTO TagsTasks(tagId, taskId) values ({tag_id}, {task_id});"
    await async_sql(insert_query)

    await tag_task_notifier(
        task_id,
        tag_id,
        'Новая задача #{task_id} {task_title} '
        'в тэге #{tag_id} {tag_title}: {date} ✅',
    )

    return ConversationHandler.END

def add_tag_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_tag_task", start_add_tag_task_callback)],
        states={
            ADD_TASK_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_id_callback)
            ],
            ADD_TAG_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_tag_id_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_tag_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
