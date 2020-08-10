from bot import bot
from telebot import types
from datetime import datetime
from site_parser import get_questions
from config import URL
from repositories import SubscribersRepository, PostsArchiveRepository, LogsRepository
from shared_methods import send_question
import sticker_ids


logs_repository = LogsRepository()


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_sticker(message.chat.id, sticker_ids.hello)
    bot.send_message(message.chat.id, 'Вас приветствует Томочка Лапочка!\n\n' + \
        '/top - получить несколько первых постов\n\n' + \
        '/notifications - подписка на рассылку новых постов\n\n' + \
        '/random - показать случайный пост')

    logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'command': message.text, 'time': datetime.now() })


@bot.message_handler(commands=['top'])
def handle_top_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    top1 = types.InlineKeyboardButton('Top 1', callback_data='top1')
    top3 = types.InlineKeyboardButton('Top 3', callback_data='top3')
    top5 = types.InlineKeyboardButton('Top 5', callback_data='top5')
    top10 = types.InlineKeyboardButton('Top 10', callback_data='top10')
    cancel = types.InlineKeyboardButton('Отмена', callback_data='topcancel')
    markup.add(top1, top3, top5, top10, cancel)
    bot.send_message(message.chat.id, 'Сколько последних постов показать??', reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data in ['top1', 'top3', 'top5', 'top10', 'topcancel'])
def process_top_command_callback(query):
    bot.delete_message(query.message.chat.id, query.message.message_id)

    if query.data == 'top1':
        count = 1
    elif query.data == 'top3':
        count = 3
    elif query.data == 'top5':
        count = 5
    elif query.data == 'top10':
        count = 10
    else:
        return

    log = { 'source': 'User message', 'from_id': query.message.chat.id, 'command': query.data, 'result': 'successfully', 'time': datetime.now() }
    bot.send_message(query.message.chat.id, f'Top {count} записей:')
    
    try:
        questions = get_questions(count)
    except:
        bot.send_message(query.message.chat.id, f'К сожалению, что-то сгнило! Попробуйте еще раз позже или посетите сайт царицы {URL}.')
        bot.send_sticker(query.message.chat.id, sticker_ids.no_mood)
        log['result'] = 'parsing failed'
        logs_repository.add(log)
        return

    for question in questions:
        send_question(bot, query.message.chat.id, question)

    logs_repository.add(log)


@bot.message_handler(commands=['notifications'])
def handle_subscribe_command(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    repository = SubscribersRepository()
    
    if repository.is_user_exists(message.from_user.id):
        subscribe = types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')
        text = 'Вы уже подписаны на рассылку. Хотите отписаться??'
    else:
        subscribe = types.InlineKeyboardButton('Подписаться', callback_data='subscribe')
        text = 'Подпишитесь на рассылку и получайте уведомления о новых постах Лапочки, как только она их опубликует!'

    cancel = types.InlineKeyboardButton('Отмена', callback_data='subscribe_cancel')
    markup.add(subscribe, cancel)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data in ['subscribe', 'unsubscribe', 'subscribe_cancel'])
def process_subscribe_command_callback(query):
    bot.delete_message(query.message.chat.id, query.message.message_id)
    repository = SubscribersRepository()

    if query.data == 'subscribe':
        repository.ensure_user(query.message.chat.id)
        text = 'Вы успешно подписаны на!!'
    elif query.data == 'unsubscribe':
        repository.delete_user(query.message.chat.id)
        text = 'Вы успешно отписаны от!!'
    else:
        return

    bot.send_message(query.message.chat.id, text)
    bot.send_sticker(query.message.chat.id, sticker_ids.done)

    logs_repository.add({ 'source': 'User message', 'from_id': query.message.chat.id, 'command': query.data, 'time': datetime.now() })


@bot.message_handler(commands=['random'])
def handle_random_command(message):
    archive = PostsArchiveRepository()
    question = archive.get_random()
    send_question(bot, message.chat.id, question)

    logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'command': message.text, 'time': datetime.now() })


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if any(word in message.text.lower() for word in ['закружился', 'закружилась', 'кружусь', 'кружимся', 'кружится']):
        bot.send_animation(message.chat.id, open('files/zakruzhilas.mp4', 'rb'))
    else:
        bot.send_message(message.chat.id, 'Неподдерживаемая команда!!')
        bot.send_sticker(message.chat.id, sticker_ids.loh)

    logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'text': message.text, 'time': datetime.now() })


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    bot.send_sticker(message.chat.id, sticker_ids.rachal)


if __name__ == '__main__':
    bot.polling(none_stop=True)