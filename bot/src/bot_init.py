from typing import List

import asyncpg

from src.handlers.create.add_task_handler import add_task_builder
from src.handlers.create.add_tag_handler import add_tag_builder
from src.handlers.create.add_user_tag_handler import add_user_tag_builder
from src.handlers.create.add_user_task_handler import add_user_task_builder
from src.handlers.create.add_tag_task_handler import add_tag_task_builder

from src.handlers.create.add_task_done_handler import add_task_done_builder

from src.handlers.delete.delete_tag_handler import delete_tag_builder
from src.handlers.delete.delete_task_handler import delete_task_builder
from src.handlers.delete.delete_tag_task_handler import delete_tag_task_builder
from src.handlers.delete.delete_user_tag_handler import delete_user_tag_builder
from src.handlers.delete.delete_user_task_handler import delete_user_task_builder

from src.handlers.get.get_gantt_diagram_handler import get_gantt_diagram_builder
from src.handlers.get.get_tasks_handler import get_tasks_builder
from src.handlers.ical.ical_handler import get_ical_builder

from src.handlers.notify.deadline_notifier import deadline_notifier

from telegram import BotCommand, Bot
from telegram.ext import (
    CommandHandler,
    Application,
    PreCheckoutQueryHandler
)

from src.handlers.handlers import *
from src.data_init import TOKEN
from src.db.connection import *
from src.models import *

import asyncio


SECS_PER_NOTIFIER = 10


async def init_pool(app):
    POOL[0] = await asyncpg.create_pool(
        host=HOST,
        database=DATABASE,
        user=USER,
        password=PASSWORD,
        port=PORT
    )


def bot_start() -> None:
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start_callback))
    application.add_handler(CommandHandler("help", help_callback))
    application.add_handler(CommandHandler("cancel", cancel_callback))

    # Create
    application.add_handler(add_task_builder())
    application.add_handler(add_tag_builder())
    application.add_handler(add_user_tag_builder())
    application.add_handler(add_tag_task_builder())
    application.add_handler(add_user_task_builder())

    application.add_handler(add_task_done_builder())

    # Delete
    application.add_handler(delete_tag_builder())
    application.add_handler(delete_task_builder())
    application.add_handler(delete_tag_task_builder())
    application.add_handler(delete_user_tag_builder())
    application.add_handler(delete_user_task_builder())

    # Get
    application.add_handler(get_gantt_diagram_builder())
    application.add_handler(get_tasks_builder())

    application.add_handler(get_ical_builder())

    application.job_queue.run_repeating(deadline_notifier, SECS_PER_NOTIFIER, 1)

    __init_commands(
        application,
        [
            BotCommand("start", "Начать"),
            BotCommand("help", "Помогите"),

            BotCommand("add_task", "Добавить задачу"),
            BotCommand("add_tag", "Добавить тэг"),
            BotCommand("tag_subscribe", "Подписаться на тэг"),
            BotCommand("task_subscribe", "Подписаться на задачу"),
            BotCommand("add_tag_task", "Добавить задачу к тэгу"),

            BotCommand("do_task", "Выполнить задачу"),

            BotCommand("delete_tag", "Удалить тэг"),
            BotCommand("delete_task", "Удалить задачу"),
            BotCommand("delete_tag_task", "Удалить задачу из тэга"),
            BotCommand("tag_unsubscribe", "Отписаться от тэга"),
            BotCommand("task_unsubscribe", "Описаться от задачи"),

            BotCommand("get_gantt_diagram", "Сгенерировать диаграмму Ганта"),
            BotCommand("get_tasks", "Получить все задачи"),

            BotCommand("get_ical", "Создать календарь"),
            
            BotCommand("cancel", "Галя, у нас отмена"),
        ]
    )

    application.post_init = init_pool

    application.run_polling()


def __init_commands(application, commands: List[BotCommand]):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.bot.set_my_commands(commands))