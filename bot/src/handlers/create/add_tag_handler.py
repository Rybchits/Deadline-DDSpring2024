from telegram import (
    Update,
)

from telegram.ext import (
    CommandHandler,
    ContextTypes,
    MessageHandler,
    ConversationHandler,
    filters,
)

from src.handlers.handlers import cancel_callback
from src.db.helpers import async_sql

START, ADD_TAG_NAME = range(2)

async def start_add_tag_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите название тэга: 🏷️")
    return ADD_TAG_NAME

# Каждый user, который добавляет тег становится его админом
# Добавляем в таблицы tags и userstags
async def add_tag_title_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.chat_id
    title = update.message.text

    insert_tag_query = f"""
        WITH newtag AS (
            INSERT INTO tags(title) values ('{title}') RETURNING id
        )
        INSERT INTO userstags(userid, tagid, is_admin)
            SELECT {user_id}, newtag.id, True FROM newtag
        RETURNING tagid;
    """

    tag_id = await async_sql(insert_tag_query)
    tag_id = tag_id[0]['tagid']

    await update.message.reply_text(f'Тэг {title} с идентификатором {tag_id}')

    return ConversationHandler.END

def add_tag_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_tag", start_add_tag_callback)],
        states={
            ADD_TAG_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_tag_title_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_tag_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
