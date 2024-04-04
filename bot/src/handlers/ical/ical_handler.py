async def start_get_ical_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.chat_id

    query = "SELECT Task.id, Tasks.title, Tasks.start, Tasks.finish, Task.description FROM Tasks JOIN UsersTasks ON Tasks.id = UsersTasks.taskId WHERE UsersTasks.userId=%s UNION (select Tasks.title, Tasks.start, Tasks.finish from tagstasks join userstags on tagstasks.tagid=userstags.tagid join tasks on tasks.id=tagstasks.taskid where userstags.userid=%s);"
    tasks = run_sql(query, (user_id, user_id))

    if not tasks:
        await update.message.reply_text("У вас нет активных задач.")
        return ConversationHandler.END

    ical_request_data = {
        "name": user_id,
        "tasks": [{
            "id": task[0],
            "title": task[1],
            "start": task[2],
            "end": task[3],
            "description": task[4]
        } for task in tasks]
    }

    response = requests.post("http://localhost:8082/ical", json=ical_request_data)
    if response.status_code == 200:
        await context.bot.send_document(user_id, document=open(f'./ical/calendars/{user_id}.ics', 'rb'))
    else:
        await update.message.reply_text("Не удалось получить данные с сервера.")

    return ConversationHandler.END

def get_ical_builder() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[CommandHandler("get_ical", start_get_ical_callback)],
        states={
            START: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_get_tasks_callback)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel_callback)]
    )