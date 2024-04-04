from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from src.db.helpers import run_sql

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("""
/add_task: Добавить новое задание. 📝

/add_tag: Придумать креативный тэг для задачи. 🏷️

/tag_subscribe: Подписаться на уведомления о задачах с определенным тэгом. 📬

/task_subscribe: Подписаться на уведомления о конкретной задаче. 📌

/add_tag_task: Привязать задачу к тэгу и добавить немного магии. ✨

/do_task: Отметить задачу как выполненную. 🎉

/delete_tag: Удалить ненужный тэг и освободить место для нового. ❌

/delete_task: Удалить задачу и избавиться от лишних хлопот. 🗑️

/delete_tag_task: Перестать связывать тэги с задачами. 🚫

/tag_unsubscribe: Отписаться от уведомлений о задачах с определенным тэгом. 🙅

/task_unsubscribe: Отписаться от уведомлений о конкретной задаче. 🚫

/get_gantt_diagram: Получить красочную диаграмму Ганта с вашими задачами. 📊

/get_tasks: Получить список всех задач и вдохновиться. 📋

/get_ical: Получить ссылку на календарь для синхронизации и легкости в планировании. 📅
                                    """
                                    )

    await context.bot.send_photo(update.message.chat_id, photo='https://cdn.discordapp.com/attachments/1224385568608354462/1225521137287434362/21kqbw.png?ex=66216e80&is=660ef980&hm=74e6ec2a1e7d70c51d410231e5e709c99b1d058424300a99e9b628761cae0ec0&')

    query = "INSERT INTO users(name, userid) values (%s, %s);"
    run_sql(query, (update.message.from_user.username, update.message.chat_id))

async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    return ConversationHandler.END