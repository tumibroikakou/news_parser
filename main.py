from deta import App
from flask import Flask

from bot_loader import bot, WEBHOOK_URL, WEBHOOK_URL_PATH
from news_handler import send_news_main, send_news_list, send_news_selected, get_latest_news
from start_handler import send_welcome
from flask_routes import index, webhook


def register_handlers():
    bot.register_message_handler(send_welcome, commands=['start', 'help'])
    bot.register_message_handler(send_news_main, commands='news')
    bot.register_message_handler(send_news_selected, commands='news_selected')
    bot.register_message_handler(send_news_list, commands='news_list')
    bot.register_message_handler(get_latest_news, commands='renew')


app = App(Flask(__name__))


@app.lib.cron()
def cron_job(event):
    get_latest_news()
    send_news_list(334499755, True)


def register_flask_routes():
    # app.add_url_rule('/', methods=['GET', 'HEAD'], view_func=index)
    app.add_url_rule(WEBHOOK_URL_PATH, methods=['POST'], view_func=webhook)


register_handlers()
register_flask_routes()
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL + WEBHOOK_URL_PATH, drop_pending_updates=True)
