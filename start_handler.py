from bot_loader import bot


def send_welcome(message):
    from_group = message.chat.id != message.from_user.id
    if not from_group:
        bot.send_message(
            message.chat.id, f'Привет {message.from_user.first_name}!\
            \nЧтобы узнать последние новости из мира фото отправь команду /news')
