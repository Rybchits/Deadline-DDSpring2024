from datetime import datetime
from telegram import (
    Update,
    ReplyKeyboardRemove
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
from src.db.helpers import run_sql

START, ADD_TASK_NAME, ADD_TASK_START_DATE, ADD_TASK_END_DATE = range(4)

async def start_add_task_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    await update.message.reply_text("Введите название задачи:")
    return ADD_TASK_NAME


async def add_task_name_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["TITLE"] = update.message.text

    await update.effective_message.reply_text("Введите дату начала задачи\t\t\t", reply_markup=create_calendar())
    
    return ADD_TASK_START_DATE


async def add_task_end_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.callback_query.from_user.id
    selected,date = await process_calendar_selection(update, context)
    # TODO добавить проверку, что дата окончания не старше даты начала
    if selected:
        await context.bot.send_message(chat_id=user_id,
                        text=f"Дата окончания выбрана: {date.strftime("%d/%m/%Y")}",
                        reply_markup=ReplyKeyboardRemove())
        
    context.user_data["FINISH"] = date

    task = context.user_data
    insert_query = "INSERT INTO tasks(title, start, finish) values (%s, %s, %s) RETURNING id;"
    task_id = run_sql(insert_query, (task["TITLE"], task["START"], task["FINISH"]))[0][0]

    insert_link_query = "INSERT INTO userstasks(userid, taskid) values (%s, %s)"
    run_sql(insert_link_query, (user_id, task_id))

    await context.bot.send_message(
        chat_id=user_id, 
        text=f'Создана задача {task["TITLE"]} с идентификатором {task_id}')
    
    return ConversationHandler.END


async def add_task_start_date_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected,date = await process_calendar_selection(update, context)
    if selected:
        await context.bot.send_message(chat_id=update.callback_query.from_user.id,
                        text=f"Дата начала выбрана: {date.strftime("%d/%m/%Y")}",
                        reply_markup=ReplyKeyboardRemove())
        
    context.user_data["START"] = date

    await update.effective_message.reply_text(text="Введите дату окончания задачи\t\t\t", reply_markup=create_calendar())
    
    return ADD_TASK_END_DATE


def add_task_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("add_task", start_add_task_callback)],
        states={
            ADD_TASK_END_DATE: [
                CallbackQueryHandler(add_task_end_date_callback)
            ],
            ADD_TASK_START_DATE: [
                CallbackQueryHandler(add_task_start_date_callback)
            ],
            ADD_TASK_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, add_task_name_callback)
            ],
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_add_task_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )
