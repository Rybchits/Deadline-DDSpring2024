import random
from datetime import datetime, timedelta
import locale

from telegram.ext import CallbackContext

from src.handlers.bot import BOT
from src.db.connection import POOL


locale.setlocale(locale.LC_ALL, "ru_RU.UTF-8")


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
            "Осталось меньше дня",
        ),
        (
            timedelta(0, 3600),  # 1 hour
            [
                "Будь готов!",
                "Самое время заканчивать:/",
                "Дедлайн пришел!",
                "PI-PI-PING!",
            ],
            "Осталось меньше часа",
        ),
    ],
    key=lambda x: x[0],
    reverse=True,
)

COUNT_NOTIFICATIONS = "(" + "(finish < '{}'::timestamptz)::int".join(" + ") + ")"
BITMASK = f"B'{'1' * 8}'::bit(8)"


async def deadline_notifier(context: CallbackContext):
    async with POOL[0].acquire() as conn:
        now = datetime.now().astimezone()
        max_past = now + NOTIFICATIONS[0][0]
        dates = [str(now + ns[0]) for ns in NOTIFICATIONS]
        count_notifications = COUNT_NOTIFICATIONS.format(*dates)

        async with conn.transaction():
            recs = await conn.fetch(
                f"""
                WITH
                Prev AS (
                    SELECT id, notified as prevNotified FROM Tasks
                        WHERE finish BETWEEN '{now}' and '{max_past}'
                ),
                TasksToNotify AS (
                    UPDATE Tasks SET notified = {count_notifications}
                        FROM Prev
                        WHERE Prev.id = Tasks.id and
                            notified < {count_notifications}
                    RETURNING
                        Tasks.id as id,
                        title,
                        finish,
                        Tasks.notified as notified,
                        ({BITMASK} >> Prev.prevnotified)
                            & ~({BITMASK} >> Tasks.notified) as mask
                )
                SELECT TasksToNotify.id as taskId,
                       MAX(TasksToNotify.title) as title,
                       MAX(TasksToNotify.finish) as finish,
                       MAX(TasksToNotify.notified) as notified,
                       GREATEST(UsersTags.userId, UsersTasks.userId) as userId
                    FROM TasksToNotify
                    LEFT JOIN TagsTasks
                        ON TagsTasks.taskId = TasksToNotify.id
                    LEFT JOIN UsersTags
                        ON UsersTags.tagId = TagsTasks.tagId and
                           (UsersTags.mask & TasksToNotify.mask)::INT::BOOL
                    LEFT JOIN UsersTasks
                        ON UsersTasks.taskId = TasksToNotify.id
                    WHERE UsersTasks.done is NULL or (
                            NOT UsersTasks.done and
                            (UsersTasks.mask & TasksToNotify.mask)::INT::BOOL
                          )
                    GROUP BY TasksToNotify.id,
                             GREATEST(UsersTags.userId, UsersTasks.userId)
                    HAVING GREATEST(UsersTags.userId, UsersTasks.userId) IS
                        NOT NULL
                """
            )

        for rec in recs:
            ind = rec["notified"] - 1
            message = (
                f"{random.choice(NOTIFICATIONS[ind][1])} "
                f"{NOTIFICATIONS[ind][2]}\n"
                f"#{rec['taskid']} {rec['title']}: "
                f"{rec['finish'].astimezone().strftime('%a, %d %b %H:%M')}"
            )

            await BOT.send_message(text=message, chat_id=rec["userid"])
