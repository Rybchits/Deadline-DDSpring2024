import random
from datetime import datetime, timedelta
import locale

import psycopg2.extras
from telegram.ext import CallbackContext

from src.db.connection import conn
from src.handlers.bot import BOT


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


NOTIFICATIONS = sorted(
    [
        (
            timedelta(1),  # 1 day
            [
                "Ты готов?",
                "Самое время начать:)",
                "Дедлайн близко...",
                "Gentle ping!",
            ],
        ),
        (
            timedelta(0, 3600),  # 1 hour
            [
                "Будь готов!",
                "Самое время заканчивать:/",
                "Дедлайн пришел!",
                "PI-PI-PING!",
            ],
        ),
    ],
    key=lambda x: x[0],
    reverse=True
)

COUNT_NOTIFICATIONS = '(' + '(finish < %s)::int'.join(' + ') + ')'


async def deadline_notifier(context: CallbackContext):
    now = datetime.now()
    dates = [str(now + ns[0]) for ns in NOTIFICATIONS]
    dates = dates + dates + [str(now), (now) + NOTIFICATIONS[0][0]]

    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
    cur.execute(
        f"""
                UPDATE Tasks SET notified = {COUNT_NOTIFICATIONS}
                WHERE notified < {COUNT_NOTIFICATIONS} and
                    finish BETWEEN %s and %s
                RETURNING id, title, notified, finish
        """,
        dates,
    )
    conn.commit()
    tasks = cur.fetchall()

    for task in tasks:
        message = (
          f'{random.choice(NOTIFICATIONS[task.notified - 1][1])}\n'
          f'#{task.id} {task.title}: {task.finish.strftime('%a, %d %b %H:%M')}'
        )

        cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)
        cur.execute(
            """
            SELECT userId FROM UsersTasks
                WHERE taskId = %(task_id)s and done = FALSE
            UNION
            (SELECT DISTINCT userId FROM UsersGroups
                JOIN GroupsTasks ON UsersGroups.groupId = GroupsTasks.groupId
                WHERE GroupsTasks.taskId = %(task_id)s
            EXCEPT
            SELECT userId FROM UsersTasks
                WHERE taskId = %(task_id)s and done = TRUE)
            """,
            {"task_id": task.id},
        )
        # conn.commit()
        users = cur.fetchall()

        for user in users:
            await BOT.send_message(text=message, chat_id=user.userid)

    conn.commit()
