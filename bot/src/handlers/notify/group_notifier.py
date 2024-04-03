import psycopg2.extras
from telegram import Bot

from src.db.connection import conn
from src.handlers.bot import BOT


async def group_task_notifier(
    task_id: int, group_id: int, message: str
) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    cur.execute(
        "SELECT userId FROM UsersGroups WHERE groupId = %s",
        (group_id,),
    )
    users = cur.fetchall()

    cur.execute(
        "SELECT title, finish FROM Tasks WHERE id = %s",
        (task_id,),
    )
    task_title, date = cur.fetchone()
    date = date.strftime('%a, %d %b %H:%M')

    cur.execute(
        "SELECT title FROM Groups WHERE id = %s",
        (group_id,),
    )
    group_title = cur.fetchone().title

    for user in users:
        await BOT.send_message(
            text=message.format(
                task_id=task_id,
                task_title=task_title,
                group_id=group_id,
                group_title=group_title,
                date=date,
            ),
            chat_id=user.userid,
        )
