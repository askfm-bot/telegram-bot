import re
from datetime import datetime, timedelta
from bot import bot
from telebot import types
from config import URL_FEED
from models import BotUser, QuestionQueueItem, QuestionQueueItemStatus
from repositories import BotUsersRepository, PostsArchiveRepository, QuestionQueueRepository, LogsRepository
import tools.site_parser as site_parser
import tools.question_asker as question_asker
import tools.incoming_message_parser as message_parser
from tools.incoming_message_parser import MessageType
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
    try:
        parsing_result = message_parser.parse(message.text)

        if parsing_result.type == MessageType.UnsupportedCommand:
            bot.send_message(message.chat.id, 'Неподдерживаемая команда!!')
            bot.send_sticker(message.chat.id, sticker_ids.loh)
            return

        if parsing_result.type == MessageType.ZakruzhilasCommand:
            bot.send_animation(message.chat.id, open('files/zakruzhilas.mp4', 'rb'))
            return

        if parsing_result.type == MessageType.InstantQuestion:
            if parsing_result.is_valid:
                markup = types.InlineKeyboardMarkup(row_width=2)
                confirm_button = types.InlineKeyboardButton('Задать!!', callback_data='instant_question')
                cancel_button = types.InlineKeyboardButton('Отмена', callback_data='instant_cancel')
                markup.add(confirm_button, cancel_button)
                text = 'Подтвердите, что хотите задать вопрос прямо сейчас:\n\n' + parsing_result.question
                bot.send_message(message.chat.id, text, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, parsing_result.comment)
            return

        if parsing_result.type == MessageType.ScheduledQuestion:
            if parsing_result.is_valid:
                markup = types.InlineKeyboardMarkup(row_width=2)
                confirm_button = types.InlineKeyboardButton('Запланировать!!', callback_data='scheduled_question')
                cancel_button = types.InlineKeyboardButton('Отмена', callback_data='scheduled_cancel')
                markup.add(confirm_button, cancel_button)
                text = f'Подтвердите, что хотите запланировать вопрос на {parsing_result.planned_time_str}:\n\n' + parsing_result.question
                bot.send_message(message.chat.id, text, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, parsing_result.comment)
            return
    finally:
        logs_repository.add({ 'source': 'User message', 'from_id': message.chat.id, 'text': message.text, 'time': datetime.utcnow() })


@bot.callback_query_handler(lambda query: query.data in ['instant_question', 'scheduled_question', 'instant_cancel', 'scheduled_cancel'])
def process_ask_question_callback(query):
    if query.data in ['instant_cancel', 'scheduled_cancel']:
        bot.delete_message(query.message.chat.id, query.message.message_id)
        return

    edited_text = 'Спрашиваем...' if query.data == 'instant_question' else 'Планируем...'
    bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=edited_text)
    message_parts = query.message.text.split('\n', maxsplit=1)
    text = message_parts[1].strip()
    full_name, username = get_user_names(query.message.chat)
    added_by_name = full_name if full_name else (username if username else query.message.chat.id)
    now = datetime.utcnow()

    if query.data == 'instant_question':
        try:
            question_asker.ask(text)
            questions_queue_repository.add(
                QuestionQueueItem(
                    text=text,
                    time_created=now,
                    time_planned=now,
                    time_sended=now,
                    status=QuestionQueueItemStatus.InstantlyInserted,
                    added_by_id=query.message.chat.id,
                    added_by_name=added_by_name,
                    has_answer=False
                )
            )
        except:
            bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text='К сожалению, что-то сгнило!')
    else:
        regex = re.compile(r'^.+(?P<datetime>\d\d\.\d\d\.\d\d\d\d\s+\d\d\:\d\d):$')
        match = regex.match(message_parts[0])
        planned_time = datetime.strptime(match.group('datetime'), '%d.%m.%Y %H:%M') - timedelta(hours=3)
        questions_queue_repository.add(
            QuestionQueueItem(
                text=text,
                time_created=now,
                time_planned=planned_time,
                time_sended=None,
                status=QuestionQueueItemStatus.Unprocessed,
                added_by_id=query.message.chat.id,
                added_by_name=added_by_name,
                has_answer=False
            )
        )

    bot.delete_message(query.message.chat.id, query.message.message_id)
    bot.send_sticker(query.message.chat.id, sticker_ids.done)


@bot.message_handler(content_types=['sticker'])
def handle_sticker(message):
    bot.send_sticker(message.chat.id, sticker_ids.rachal)


if __name__ == '__main__':
    bot.polling(none_stop=True)