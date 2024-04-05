from datetime import datetime, timedelta
import gantt
from cairosvg import svg2png

from typing import List

from telegram import (Update)

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

# Строит диаграмму Ганта на две недели вперед
def build_gantt_chart(user_id: str, tasks: List):
    gantt.define_font_attributes(fill='black', stroke='black', stroke_width=0, font_family="CenturyGothic")

    path=f'./charts/user_chart_{user_id}'

    project = gantt.Project(color="#FFA500")
    for task in tasks:
        project.add_task(gantt.Task(name=task[0], start=datetime.date(task[1]), stop=datetime.date(task[2])))

    project.make_svg_for_tasks(
        filename=path + '.svg',
        today=datetime.today(), 
        start=(datetime.today() - timedelta(days=10)).date(), 
        end=(datetime.today() + timedelta(days=31)).date())
    
    svg2png(url=path + '.svg', write_to=path + '.png')


async def start_get_gantt_diagram_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.message.chat_id

    query = "SELECT Tasks.title, Tasks.start, Tasks.finish FROM Tasks JOIN UsersTasks ON Tasks.id = UsersTasks.taskId WHERE UsersTasks.userId=%s UNION (select Tasks.title, Tasks.start, Tasks.finish from tagstasks join userstags on tagstasks.tagid=userstags.tagid join tasks on tasks.id=tagstasks.taskid where userstags.userid=%s);"
    tasks = run_sql(query, (chat_id, chat_id))

    if not tasks:
        await update.message.reply_text("У вас нет активных задач. 🥳")
        return ConversationHandler.END
    
    build_gantt_chart(chat_id, tasks)
    await update.message.reply_text("Мистер Гантт к вашим услугам! 🙇")
    await context.bot.send_photo(chat_id, photo=open(f'./charts/user_chart_{chat_id}.png', 'rb'))

    return ConversationHandler.END

def get_gantt_diagram_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("get_gantt_diagram", start_get_gantt_diagram_callback)],
        states={
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_get_gantt_diagram_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )