from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler,
)

from src.handlers.handlers import cancel_callback
from src.db.helpers import async_sql

START, ADD_TAG_ID = range(2)


async def start_add_user_tag_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = update.message.chat_id
    sql_query = f"""
        SELECT Tags.title, Tags.id FROM Tags 
            LEFT JOIN UsersTags ON Tags.id = UsersTags.tagId and UsersTags.userId = {user_id}
        WHERE tagId IS NULL
    """
    user_tags = await async_sql(sql_query)
    print(user_tags)
    if not user_tags:
        await update.message.reply_text("Нет доступных тэгов для подписки 🙂")
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

    await update.effective_message.reply_text("Укажите название тэга: 🏷️", reply_markup=reply_markup)
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

    tag_id = int(query.data)
    user_id = query.message.chat_id

    sql_query = f"SELECT title from Tags WHERE id={tag_id};"
    tag_title = await async_sql(sql_query)
    tag_title = tag_title[0]["title"]

    sql_query = f"""
        INSERT INTO UsersTags(userId, tagId, is_admin)
            VALUES ({user_id}, {tag_id}, False);
    """
    await async_sql(sql_query)

    await query.message.reply_text(f"Вы успешно подписались на тэг {tag_title}! 🎉", reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def add_user_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("tag_subscribe", start_add_user_tag_callback)],
        states={
            ADD_TAG_ID: [
                CallbackQueryHandler(add_tag_id_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)],
    )
