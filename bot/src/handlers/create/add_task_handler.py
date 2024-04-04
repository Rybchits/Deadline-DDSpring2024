from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
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

from src.calendar import create_calendar, process_calendar_selection

from src.handlers.handlers import cancel_callback
from src.db.helpers import async_sql


START, ADD_TASK_NAME, ADD_TASK_END_TIME, ADD_TASK_END_DATE = range(4)


async def start_add_task_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    await update.message.reply_text("Введите название задачи:")
    return ADD_TASK_NAME


async def add_task_name_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    context.user_data["TITLE"] = update.message.text

    context.user_data["START"] = datetime.now()

    await update.effective_message.reply_text(
        text="Введите дату окончания задачи\t\t\t", reply_markup=create_calendar()
    )

    return ADD_TASK_END_DATE


async def add_task_end_date_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_id = update.callback_query.from_user.id
    selected, date = await process_calendar_selection(update, context)

    if selected:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"Дата окончания выбрана: {date.strftime('%d/%m/%Y')}",
            reply_markup=ReplyKeyboardRemove(),
        )

    context.user_data["FINISH"] = date

    timestr = lambda x: f"0{str(x)}"[-2:]
    keyboard = [
        [
            InlineKeyboardButton(
                f"{timestr(i * 4 + j)}:00",
                callback_data=i * 4 + j,
            )
            for j in range(4)
        ]
        for i in range(6)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.effective_message.reply_text(
        "Введите время окончания задачи:", reply_markup=reply_markup
    )

    return ADD_TASK_END_TIME


async def add_task_end_time_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.callback_query.from_user.id

    query = update.callback_query
    ind = int(query.data)
    hour = ind

    date = context.user_data["FINISH"].replace(hour=hour)
    context.user_data["FINISH"] = date

    await context.bot.edit_message_text(
        text=query.message.text,
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
    )

    await context.bot.send_message(
        chat_id=update.callback_query.from_user.id,
        text=f"Дата выбрана: {date.strftime('%d/%m/%Y %H:%M')}",
        reply_markup=ReplyKeyboardRemove(),
    )

    if date < context.user_data["START"]:
        await context.bot.send_message(
            chat_id=user_id,
            text="Вы не можете решить задачу в прошлом, "
            "постарайтесь жить сейчас и думать о будущем",
        )
        await update.effective_message.reply_text(
            text="Введите дату окончания задачи\t\t\t", reply_markup=create_calendar()
        )
        return ADD_TASK_END_DATE

    task = context.user_data
    insert_query = """
        WITH newtask AS (
            INSERT INTO tasks(title, description, start, finish)
                VALUES ($1, 'default', $2, $3)
            RETURNING id
        )
        INSERT INTO userstasks(userid, taskid)
            SELECT $4, newtask.id FROM newtask
        RETURNING taskid;
    """

    task_id = await async_sql(
        insert_query, (task["TITLE"], task["START"], task["FINISH"], user_id)
    )
    task_id = task_id[0]["taskid"]

    await context.bot.send_message(
        chat_id=user_id,
        text=f'Создана задача {task["TITLE"]} с идентификатором {task_id}',
    )

    return ConversationHandler.END


def add_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_task", start_add_task_callback)],
        states={
            ADD_TASK_END_DATE: [CallbackQueryHandler(add_task_end_date_callback)],
            ADD_TASK_END_TIME: [CallbackQueryHandler(add_task_end_time_callback)],
            ADD_TASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_name_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)],
    )
