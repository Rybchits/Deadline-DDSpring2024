from datetime import datetime

from src.db.connection import POOL
from src.handlers.bot import BOT


async def tag_task_notifier(task_id: int, tag_id: int, message: str) -> None:
    async with POOL[0].acquire() as conn:
        async with conn.transaction():
            res = await conn.fetch(
                f"SELECT title, finish FROM Tasks WHERE id = {task_id}",
            )
            task_title, date = res[0]["title"], res[0]["finish"]
            date = date.astimezone()

            if date < datetime.now().astimezone():
                return

            users = await conn.fetch(
                f"""
                SELECT UsersTags.userId FROM UsersTags
                    LEFT JOIN UsersTasks
                        ON UsersTasks.userId = UsersTags.userId
                    WHERE tagId = {tag_id} and UsersTasks.done != TRUE
                    GROUP BY UsersTags.userId
            """
            )

            res = await conn.fetch(
                f"SELECT title FROM Tags WHERE id = {tag_id}",
            )
            tag_title = res[0]["title"]

    for user in users:
        await BOT.send_message(
            text=message.format(
                task_id=task_id,
                task_title=task_title,
                tag_id=tag_id,
                tag_title=tag_title,
                date=date,
            ),
            chat_id=user["userid"],
        )
