from functools import wraps
from config import ALLOWED_USER_IDS
from bot import bot


def validate_user(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        chat_id = args[0].chat.id
        if chat_id in ALLOWED_USER_IDS:
            fn(*args, **kwargs)
        else:
            bot.send_message(chat_id, 'У вас нет доступа к!')
    return wrapped
