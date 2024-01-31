import re
from apscheduler.schedulers.background import BackgroundScheduler

from bot_loader import bot, admins
from news_handler import send_news_main, get_latest_news, send_news_post, send_news_list
from sqlite_utils import write_job_to_db, get_all_jobs_from_db, remove_job_from_db

scheduler = BackgroundScheduler(timezone="Europe/Moscow")


def ask_schedule_time(message):  # not using at this time
    if message.from_user.id in admins:
        bot.send_message(
            message.chat.id, 'Введите время для отправки последней новости:')
        return bot.register_next_step_handler_by_chat_id(message.chat.id, schedule_job)
    else:
        bot.reply_to(
            message, f'{message.from_user.first_name} у тебя нет власти надо мной!')


def schedule_job(message) -> None:
    bot.delete_message(message.chat.id, message.message_id)
    # if message.from_user.id in admins:
    try:
        hour, minute = re.search(
            r'([0-9]|0[0-9]|1[0-9]|2[0-3])[:.!-]([0-5][0-9])', message.text).groups()
    except AttributeError as e:
        # bot.send_message(message.chat.id, 'Не указано время. Я точно знаю, охуенную регулярку написал')
        print(e)
    else:
        scheduler.add_job(send_news_main, 'cron', hour=hour, minute=minute, args=[message],
                          id=str(message.chat.id), replace_existing=True)
        is_group = 1 if message.from_user.id != message.chat.id else 0
        write_job_to_db(message.chat.id, hour, minute, is_group)
    # else:
    #     bot.reply_to(message, f'{message.from_user.first_name} у тебя нет власти надо мной!')


def latest_news_update() -> None:
    get_latest_news()
    scheduler.add_job(get_latest_news, 'interval', hours=2)


def schedule_jobs_from_db() -> None:
    for i_job in get_all_jobs_from_db():
        chat_id, hour, minute, is_group = i_job
        scheduler.add_job(send_news_post, 'cron', hour=hour, minute=minute, args=[chat_id, get_latest_news()[0],
                                                                                  is_group],
                          id=str(chat_id), replace_existing=True)


def scheduler_startup() -> None:
    latest_news_update()
    # schedule_jobs_from_db()

    # scheduler.add_job(get_latest_news, 'cron', hour=9)
    # scheduler.add_job(send_news_list, 'cron', hour=9, minute=2, args=[334499755, True],
    #                   id='334499755kbd', replace_existing=True)

    scheduler.start()


def remove_job(message) -> None:
    scheduler.remove_job(str(message.chat.id))
    remove_job_from_db(message.chat.id)


def print_jobs(message) -> None:
    bot.send_message(message.chat.id, '\n\n'.join(
        f'<b>{str(i.id)}</b> - {str(i)}' for i in scheduler.get_jobs()), parse_mode='HTML')
