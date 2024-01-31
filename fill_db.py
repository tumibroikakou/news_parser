from bot_loader import bot
from news_handler import parse_news, save_news_in_db, deta, news


fill = deta.Base('fill')
# articles = deta.Base('articles')


def fetch_news() -> list:
    result = news.fetch()
    all_news = result.items
    while result.last:
        result = news.fetch(last=result.last)
        all_news += result.items
    return all_news


def long_fill_titles():
    title = fill.get('title')
    if title:
        curr = title.get('curr')
        news_lst: list = parse_news(curr)
        save_news_in_db(news_lst)
        if curr > 0:
            curr -= 15
            return fill.put({'curr': curr}, 'title')
        return bot.send_message(369780714, f'filled! curr={curr}')
    fill.put({'curr': 5415}, 'title')


# def long_fill_articles():
    # article = fill.get('article')
    # if article:
    #     curr = article.get('curr')



def dumb_fill(max_page: int = 30) -> None:
    for i in range(max_page, -1, -15):
        news_lst: list = parse_news(i)
        save_news_in_db(news_lst)


# async def dumb_fill_async(max_page: int=45) -> None:
#     for i in range(max_page, -1, -15):
#         news_lst: list = await parse_news(i)
#         await save_news_in_db(news_lst)
