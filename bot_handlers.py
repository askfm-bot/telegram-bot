import re
from datetime import datetime, timedelta
from bot import bot
from telebot import types
from config import URL_FEED
from models import BotUser, QuestionQueueItem
from repositories import BotUsersRepository, PostsArchiveRepository, QuestionQueueRepository, LogsRepository
import tools.site_parser as site_parser
import tools.question_asker as question_asker
from shared.methods import send_question, get_user_names
import sticker_ids


bot_users_repository = BotUsersRepository()
posts_archive_repository = PostsArchiveRepository()
questions_queue_repository = QuestionQueueRepository()
logs_repository = LogsRepository()


@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.send_sticker(message.chat.id, sticker_ids.hello)
    bot.send_message(message.chat.id, 'Вас приветствует Томочка Лапочка!\n\n' + \
        '/top - получить несколько первых постов\n\n' + \
        '/notifications - подписка на рассылку новых постов\n\n' + \
        '/random - показать случайный пост')

    full_name, username = get_user_names(message.chat)
    bot_users_repository.ensure(BotUser(message.chat.id, full_name, username, True))

    logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'command': message.text, 'time': datetime.utcnow() })


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

    log = { 'source': 'User message', 'from_id': query.message.chat.id, 'command': query.data, 'result': 'successfully', 'time': datetime.utcnow() }
    bot.send_message(query.message.chat.id, f'Top {count} записей:')
    
    try:
        questions = site_parser.get_questions(count)
    except:
        bot.send_message(query.message.chat.id, f'К сожалению, что-то сгнило! Попробуйте еще раз позже или посетите сайт царицы {URL_FEED}.')
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
    user = bot_users_repository.get_by_id(message.from_user.id)

    if user.is_subscribed_to_notifications:
        subscribe = types.InlineKeyboardButton('Отписаться', callback_data='unsubscribe')
        text = 'Вы уже подписаны на рассылку и получаете уведомления о новых постах Лапочки, как только она их опубликует! Хотите отписаться??'
    else:
        subscribe = types.InlineKeyboardButton('Подписаться', callback_data='subscribe')
        text = 'Подпишитесь на рассылку и получайте уведомления о новых постах Лапочки, как только она их опубликует!'

    cancel = types.InlineKeyboardButton('Отмена', callback_data='subscribe_cancel')
    markup.add(subscribe, cancel)
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.callback_query_handler(lambda query: query.data in ['subscribe', 'unsubscribe', 'subscribe_cancel'])
def process_subscribe_command_callback(query):
    bot.delete_message(query.message.chat.id, query.message.message_id)

    if query.data == 'subscribe':
        bot_users_repository.update_is_subscribed(query.message.chat.id, True)
        text = 'Вы успешно подписаны на!!'
    elif query.data == 'unsubscribe':
        bot_users_repository.update_is_subscribed(query.message.chat.id, False)
        text = 'Вы успешно отписаны от!!'
    else:
        return

    bot.send_message(query.message.chat.id, text)
    bot.send_sticker(query.message.chat.id, sticker_ids.done)

    logs_repository.add({ 'source': 'User message', 'from_id': query.message.chat.id, 'command': query.data, 'time': datetime.utcnow() })


@bot.message_handler(commands=['random'])
def handle_random_command(message):
    question = posts_archive_repository.get_random()
    send_question(bot, message.chat.id, question)

    logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'command': message.text, 'time': datetime.utcnow() })


@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text.startswith('-q'):
        pattern = re.compile(r'^-q\s+(?P<datetime>\d\d\.\d\d\.\d\d\d\d\s+\d\d:\d\d)(?P<text>[\s\S]+)$')
        match = pattern.match(message.text)
        if match:
            try:
                planned_time_str = match.group('datetime')
                time_planned = datetime.strptime(planned_time_str, '%d.%m.%Y %H:%M')
                now = datetime.utcnow() + timedelta(hours=3)
                if time_planned < now:
                    now_str = now.strftime('%d.%m.%Y %H:%M')
                    time_planned_str = time_planned.strftime('%d.%m.%Y %H:%M')
                    bot.send_message(message.chat.id, f'Необходимо указать время из будущего! Время на сервере {now_str}, а вы указали {time_planned_str}.')
                    return
                text = match.group('text').strip()
                confirm_message = f'Подтвердите, что хотите запланировать вопрос на {planned_time_str}:\n\n'
                send = types.InlineKeyboardButton('Запланировать!!', callback_data='plan_question')
            except:
                bot.send_message(message.chat.id, 'Вы указали некорректное время!')
                return
        else:
            text = message.text[2:].strip()
            confirm_message = 'Подтвердите, что хотите задать вопрос прямо сейчас:\n\n'
            send = types.InlineKeyboardButton('Задать!!', callback_data='send_question')
        markup = types.InlineKeyboardMarkup(row_width=2)
        cancel = types.InlineKeyboardButton('Отмена', callback_data='ask_cancel')
        markup.add(send, cancel)
        bot.send_message(message.chat.id, confirm_message + text, reply_markup=markup)
        return

    if any(word in message.text.lower() for word in ['закружился', 'закружилась', 'кружусь', 'кружимся', 'кружится']):
        bot.send_animation(message.chat.id, open('files/zakruzhilas.mp4', 'rb'))
    else:
        bot.send_message(message.chat.id, 'Неподдерживаемая команда!!')
        bot.send_sticker(message.chat.id, sticker_ids.loh)

    logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'text': message.text, 'time': datetime.utcnow() })


@bot.callback_query_handler(lambda query: query.data in ['send_question', 'plan_question', 'ask_cancel'])
def process_ask_question_callback(query):
    if query.data == 'ask_cancel':
        bot.delete_message(query.message.chat.id, query.message.message_id)
        return

    edited_text = 'Спрашиваем...' if query.data == 'send_question' else 'Планируем...'
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=edited_text)
    message_parts = query.message.text.split('\n', maxsplit=1)
    text = message_parts[1].strip()
    full_name, username = get_user_names(query.message.chat)
    added_by_name = full_name if full_name else (username if username else query.message.chat.id)

    if query.data == 'send_question':
        try:
            question_asker.ask(text)
            now =  datetime.utcnow()
            questions_queue_repository.add(QuestionQueueItem(text, now, now, now, 4, query.message.chat.id, added_by_name, False))
        except:
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text='К сожалению, что-то сгнило!')
    else:
        regex = re.compile(r'^.+(?P<datetime>\d\d\.\d\d\.\d\d\d\d\s+\d\d\:\d\d):$')
        match = regex.match(message_parts[0])
        planned_time = datetime.strptime(match.group('datetime'), '%d.%m.%Y %H:%M') - timedelta(hours=3)
        questions_queue_repository.add(QuestionQueueItem(text, datetime.utcnow(), planned_time, None, 0, query.message.chat.id, added_by_name, False))

    bot.delete_message(query.message.chat.id, query.message.message_id)
    bot.send_sticker(query.message.chat.id, sticker_ids.done)


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    bot.send_sticker(message.chat.id, sticker_ids.rachal)


if __name__ == '__main__':
    bot.polling(none_stop=True)