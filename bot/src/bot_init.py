from typing import List

from src.handlers.create.add_task_handler import add_task_builder
from src.handlers.create.add_group_handler import add_group_builder
from src.handlers.create.add_user_group_handler import add_user_group_builder
from src.handlers.create.add_user_task_handler import add_user_task_builder
from src.handlers.create.add_group_task_handler import add_group_task_builder

from src.handlers.create.add_task_done_handler import add_task_done_builder

from src.handlers.delete.delete_group_handler import delete_group_builder
from src.handlers.delete.delete_task_handler import delete_task_builder
from src.handlers.delete.delete_group_task_handler import delete_group_task_builder
from src.handlers.delete.delete_user_group_handler import delete_user_group_builder
from src.handlers.delete.delete_user_task_handler import delete_user_task_builder

from src.handlers.get.get_gantt_diagram_handler import get_gantt_diagram_builder
from src.handlers.get.get_tasks_handler import get_tasks_builder

from src.handlers.notify.deadline_notifier import deadline_notifier

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


SECS_PER_NOTIFIER = 10


def bot_start() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_callback))
    
    # Create
    application.add_handler(add_task_builder())
    application.add_handler(add_group_builder())
    application.add_handler(add_user_group_builder())
    application.add_handler(add_group_task_builder())
    application.add_handler(add_user_task_builder())
    
    application.add_handler(add_task_done_builder())
    
    # Delete
    application.add_handler(delete_group_builder())
    application.add_handler(delete_task_builder())
    application.add_handler(delete_group_task_builder())
    application.add_handler(delete_user_group_builder())
    application.add_handler(delete_user_task_builder())
    
    # Get
    application.add_handler(get_gantt_diagram_builder())
    application.add_handler(get_tasks_builder())

    application.job_queue.run_repeating(deadline_notifier, SECS_PER_NOTIFIER, 1)

    __init_commands(
        application,
        [
            BotCommand("start", "Начать"),

            BotCommand("add_task", "Добавить задачу"),
            BotCommand("add_group", "Добавить группу"),
            BotCommand("add_user_group", "Добавить UsersGroups"),
            BotCommand("add_user_task", "Добавить UsersTasks"),
            BotCommand("add_group_task", "Добавить GroupsTasks"),

            BotCommand("do_task", "Выполнить задачу"),

            BotCommand("delete_group", "Удалить группу"),
            BotCommand("delete_task", "Удалить задачу"),
            BotCommand("delete_group_task", "Удалить GroupsTasks"),
            BotCommand("delete_user_group", "Удалить UsersGroups"),
            BotCommand("delete_user_task", "Удалить UsersTasks"),
            
            BotCommand("get_gantt_diagram", "Сгенерировать диаграмму Ганта"),
            BotCommand("get_tasks", "Получить все задачи"),
        ]
    )

    application.run_polling()


def __init_commands(application, commands: List[BotCommand]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.bot.set_my_commands(commands))