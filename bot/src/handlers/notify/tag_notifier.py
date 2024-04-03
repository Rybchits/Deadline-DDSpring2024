import psycopg2.extras
from telegram import Bot

from src.db.connection import conn
from src.handlers.bot import BOT

async def tag_task_notifier(
    task_id: int, tag_id: int, message: str
) -> None:
    cur = conn.cursor(cursor_factory=psycopg2.extras.NamedTupleCursor)

    cur.execute(
        "SELECT userId FROM UsersTags WHERE tagId = %s",
        (tag_id,),
    )
    users = cur.fetchall()

    cur.execute(
        "SELECT title, finish FROM Tasks WHERE id = %s",
        (task_id,),
    )
    task_title, date = cur.fetchone()
    date = date.strftime('%a, %d %b %H:%M')

    cur.execute(
        "SELECT title FROM Tags WHERE id = %s",
        (tag_id,),
    )
    tag_title = cur.fetchone().title

    for user in users:
        await BOT.send_message(
            text=message.format(
                task_id=task_id,
                task_title=task_title,
                tag_id=tag_id,
                tag_title=tag_title,
                date=date,
            ),
            chat_id=user.userid,
        )
