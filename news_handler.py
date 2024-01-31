from httpx import Client
from bs4 import BeautifulSoup
from telebot import types
from deta import Deta

from bot_loader import bot
from test_time import my_timer

deta = Deta()
# {'key': message.from_user.id, name: message.from_user.first_name, 'current_page': int}
users = deta.Base('users')
news = deta.Base('news')


def get_html(url) -> str:
    headers: dict = {
        "User-Agent": "Mozilla/5.001 (windows; U; NT4.0; en-US; rv:1.0) Gecko/25250101"}
    with Client(headers=headers, verify=False, timeout=11) as client:
        response = client.get(url=url)
        return response.text


def parse_news(feed_start: int = 0) -> list:
    url: str = 'https://photowebexpo.ru/'
    full_path: str = f'{url}news?feed_start={str(feed_start)}'
    soup = BeautifulSoup(get_html(full_path), 'html.parser')
    main_news: list = soup.find('div', class_='grid__container').find_all(
        'div', class_='post')
    result: list = list()
    for i_news in main_news:
        post_title = i_news.find('a', class_='post__title')
        template = {
            'cover': f"{url}{i_news.find('img', class_='post__cover-img').get('src')}",
            'link': f'{url}{post_title.get("href")}',
            'title': post_title.get_text(strip=True),
            'intro': i_news.find('div', class_='post__intro').get_text(strip=True)
        }
        result.append(template)
    return result


def pop_keys(data: list) -> list:
    for i_dict in data:
        i_dict.pop('key')
    return data


def get_four_digits_key(key: int) -> str:
    return str(key).zfill(4)


def get_max_key() -> int:
    max_key: dict = news.get('number')
    return max_key.setdefault('max', 0)


def get_news_from_db(limit: int = 15) -> list:
    max_key: int = get_max_key()
    if max_key:
        search_key: str = get_four_digits_key(max_key - (limit - 1))
        fetch_from_db = news.fetch(query={'key?gte': search_key}, limit=limit)
        return fetch_from_db.items
    return list()


def save_news_in_db(latest_news: list) -> None:
    max_key: int = get_max_key()
    last_from_db = get_news_from_db(20)
    if last_from_db:
        pop_keys(last_from_db)
    for i_new in latest_news[::-1]:
        if i_new not in last_from_db:
            max_key += 1
            news.put(i_new, get_four_digits_key(max_key))
    news.put({'max': max_key}, 'number')


def get_latest_news() -> list:
    new_news: list = parse_news()
    save_news_in_db(new_news)
    return new_news


def send_news_main(message) -> None:
    last_one: int = get_max_key()
    users.put(
        {'name': message.from_user.first_name,
         'username': message.from_user.username,
         'current_page': last_one},
        str(message.from_user.id))
    from_group: bool = message.chat.id != message.from_user.id
    if from_group:
        bot.delete_message(message.chat.id, message.message_id)
    send_news_post(message.chat.id, news.get(
        get_four_digits_key(last_one)), from_group)


def send_news_post(chat_id: int, parsed_news: dict, is_group=False) -> None:
    keyboard = types.InlineKeyboardMarkup(keyboard=[
        [types.InlineKeyboardButton('Почитать на сайте', url=parsed_news["link"])]])
    if not is_group:
        keyboard.add(
            types.InlineKeyboardButton('< Назад', callback_data='prev'),
            types.InlineKeyboardButton('Дальше >', callback_data='next')
        )
    bot.send_photo(chat_id, parsed_news['cover'],
                   f'*{parsed_news["title"]}*\n\n{parsed_news["intro"]}', parse_mode='markdown',
                   disable_notification=True, reply_markup=keyboard)


def send_news_selected(message) -> None:
    user: dict = users.get(str(message.from_user.id))
    from_group: bool = message.chat.id != message.from_user.id
    if from_group:
        bot.delete_message(message.chat.id, message.message_id)
    send_news_post(message.chat.id, news.get(
        get_four_digits_key(user.get('current_page'))), from_group) if user else None


# def next_post(message) -> callable:
#     user: dict = users.get(str(message.chat.id))
#     last_one: int = get_max_key()
#     if user:
#         page: int = user.get('current_page')
#         if page > 1:
#             page -= 1
#         # if page == news.get('number').get('max'):???
#         #     save_news_in_db(parse_news(page))
#         users.update({'current_page': page}, user.get('key'))
#     else:
#         page = last_one
#         users.put(
#             {'name': message.from_user.first_name,
#              'username': message.from_user.username,
#              'current_page': last_one},
#             str(message.from_user.id))
#     return send_news_post(message.chat.id, news.get(get_four_digits_key(page)))


# def prev_post(message) -> callable:
#     user: dict = users.get(str(message.chat.id))
#     last_one: int = get_max_key()
#     if user:
#         page: int = user.get('current_page')
#         if page < last_one:
#             page += 1
#         users.update({'current_page': page}, user.get('key'))
#     else:
#         page = last_one
#         users.put(
#             {'name': message.from_user.first_name,
#              'username': message.from_user.username,
#              'current_page': page},
#             str(message.from_user.id))
#     return send_news_post(message.chat.id, news.get(get_four_digits_key(page)))


@bot.callback_query_handler(func=lambda call: call.data in ('next', 'prev'))
def call_next_prev(call) -> callable:
    user: dict = users.get(str(call.message.chat.id))
    last_one: int = get_max_key()
    if user:
        page: int = user.get('current_page')
        if page < last_one and call.data == 'prev':
            page += 1
        elif page > 1 and call.data == 'next':
            page -= 1
        users.update({'current_page': page}, user.get('key'))
    else:
        page = last_one
        users.put(
            {'name': call.message.from_user.first_name,
             'username': call.message.from_user.username,
             'current_page': page},
            str(call.message.from_user.id))
    return send_news_post(call.message.chat.id, news.get(get_four_digits_key(page)))
    # if call.data == 'next':
    #     return next_post(call.message)
    # return prev_post(call.message)


# @bot.callback_query_handler(func=lambda call: call.data in ('next', 'prev'))
# def call_next_prev(call) -> callable:
#     if call.data == 'next':
#         return next_post(call.message)
#     return prev_post(call.message)


def send_news_to_group(call):
    selected = call.data
    # -1001747666546 - Test group
    return send_news_post(-1001518254779, news.get(selected), is_group=True)


@bot.callback_query_handler(func=send_news_to_group)
def send_news_list(message, send_to_group=False):
    limit = 15
    last_from_db: list = sorted(get_news_from_db(
        limit), key=lambda item: item.get('key'), reverse=True)

    keyboard = types.InlineKeyboardMarkup(keyboard=[])
    if send_to_group:
        kbd_row = list()
        for i, i_item in enumerate(last_from_db, 1):
            kbd_row.append(types.InlineKeyboardButton(
                str(i), callback_data=i_item.get('key')))
            if i % 5 == 0:
                keyboard.keyboard.append(kbd_row)
                kbd_row = []
    links_markdown = '\n\n'.join([f'{index}. [{i_link["title"]}]({i_link["link"]})'
                                  for index, i_link in enumerate(last_from_db, start=1)])
    msg = f'_Последние {limit} новостей с_ [PhotoWebExpo.ru](https://photowebexpo.ru)\n\n{links_markdown}'
    bot.send_message(
        message.chat.id if isinstance(message, types.Message) else message,
        msg, parse_mode='markdown', reply_markup=keyboard
    )
