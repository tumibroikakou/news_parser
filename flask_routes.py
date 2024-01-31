from flask import request, abort, jsonify
from telebot import types
from bot_loader import bot
from fill_db import fetch_news

def index():
    return ''

def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return 'OK'
    else:
        abort(403)
