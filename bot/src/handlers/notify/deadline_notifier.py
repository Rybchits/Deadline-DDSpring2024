import random
from datetime import datetime
import locale

import asyncpg
from telegram.ext import CallbackContext

from src.handlers.bot import BOT
from src.db.connection import POOL


locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


GREETINGS: 'List[str]' = [
    "Ты готов?",
    "Самое время начать:)",
    "Дедлайн близко...",
    "Gentle ping!",
]


async def deadline_notifier(context: CallbackContext) -> None:
    async with POOL[0].acquire() as conn:
        now = datetime.now()

        async with conn.transaction():
            recs = await conn.fetch(
                """
                    WITH notifications_done AS (
                        DELETE FROM UserNotification
                            WHERE popTime < $1 RETURNING *
                    )
                    SELECT Tasks.id as taskid,
                        Tasks.title as title,
                        Tasks.finish as finish,
                        notifications_done.userId as userid
                        FROM notifications_done
                        LEFT JOIN UsersTasks ON
                            UsersTasks.taskId = notifications_done.taskId and
                            UsersTasks.userId = notifications_done.userId
                        JOIN Tasks ON notifications_done.taskId = Tasks.id and
                            UsersTasks.done != TRUE
                    ;
                """,
                now,
            )

        for rec in recs:
            print(rec)
            message = (
                f'{random.choice(GREETINGS)}\n'
                f'#{rec['taskid']} {rec['title']}: {rec['finish'].strftime('%a, %d %b %H:%M')}'
            )

            await BOT.send_message(text=message, chat_id=rec['userid'])
