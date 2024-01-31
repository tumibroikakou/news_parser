from time import perf_counter
from functools import wraps

from bot_loader import bot


def my_timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_at = perf_counter()
        func_result = func(*args, **kwargs)
        end_at = perf_counter()
        msg = f'{func.__name__}, {end_at - start_at}'
        bot.send_message(369780714, msg)
        return func_result
    return wrapper

