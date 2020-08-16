import requests
from io import BytesIO

def send_question(bot, chat_id, question):
    bot.send_message(chat_id, question)
    if question.image_url:
        try:
            response = requests.get(question.image_url)
            bot.send_photo(chat_id, BytesIO(response.content))
        except:
            pass


def get_user_names(chat):
    try:
        full_name = ' '.join([chat.first_name, chat.last_name])
    except:
        full_name = None

    try:
        username = chat.username
    except:
        username = None

    return full_name, username