import telebot

from dotenv import load_dotenv
from os import environ as env

load_dotenv()

BOT_TOKEN = env.get('BOT_TOKEN')
WEBHOOK_HOST = env.get('WEBHOOK_HOST')
WEBHOOK_PORT = env.get('WEBHOOK_PORT')
WEBHOOK_LISTEN = '0.0.0.0'
WEBHOOK_URL = "https://{}".format(WEBHOOK_HOST)
WEBHOOK_URL_PATH = "/{}/".format(BOT_TOKEN)


bot = telebot.TeleBot(BOT_TOKEN)
admins = [int(v) for k, v in env.items() if k.startswith('ADMIN')]
