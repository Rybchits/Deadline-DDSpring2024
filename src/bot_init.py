from typing import List

from src.handlers.add_deadline_handler import add_deadline_builder
from src.handlers.add_user_group_handler import add_user_group_builder
from src.handlers.get_gantt_diagram_handler import get_gantt_diagram_builder
from src.handlers.get_tasks_handler import get_tasks_builder

from telegram import BotCommand, Bot
from telegram.ext import (
    CommandHandler,
    Application,
    PreCheckoutQueryHandler
)

from src.handlers.handlers import *
from src.data_init import TOKEN
from src.models import *

import asyncio

def bot_start() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(add_deadline_builder())
    application.add_handler(add_user_group_builder())
    application.add_handler(get_gantt_diagram_builder())
    application.add_handler(get_tasks_builder())

    __init_commands(
        application,
        [
            BotCommand("start", "Начать"),
            BotCommand("add_deadline", "Добавить дедлайн"),
            BotCommand("add_user_group", "Добавить группу пользователей"),
            BotCommand("get_gantt_diagram", "Сгенерировать диаграмму Ганта"),
            BotCommand("get_tasks", "Получить все задачи"),
        ]
    )

    application.run_polling()


def __init_commands(application, commands: List[BotCommand]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.bot.set_my_commands(commands))