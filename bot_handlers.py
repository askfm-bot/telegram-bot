import re
from datetime import datetime, timedelta
from bot import bot
from telebot import types
from models.bot_user import BotUser
from models.question_queue_item import QuestionQueueItem, QuestionQueueItemStatus
from repositories.bot_users_repository import BotUsersRepository
from repositories.post_archive_repository import PostsArchiveRepository
from repositories.question_queue_repository import QuestionQueueRepository
from repositories.vk_user_online_statuses_repository import VkUserOnlineStatusesRepository
from repositories.logs_repository import LogsRepository
from decorators.validation_decorator import validate_user
from tools.question_asker import QuestionAsker
from tools.site_parser import SiteParser
from tools.question_sender import QuestionSender
from tools.incoming_message_parser import IncomingMessageParser, MessageType
from tools.vk_status_plot_builder import VkStatusPlotBuilder
from tools.vk_status_plot_sender import VkStatusPlotSender
from tools.requests_notifier import RequestsNotifier
from tools.datetime_utils import DatetimeUtils
from static.user_names_extractor import UserNamesExtractor
from static.sticker_ids import StickerIds
from config import URL_FEED, TARGET_TELEGRAM_USER_ID

bot_users_repository = BotUsersRepository()
posts_archive_repository = PostsArchiveRepository()
questions_queue_repository = QuestionQueueRepository()
vk_online_status_repository = VkUserOnlineStatusesRepository()
logs_repository = LogsRepository()

requests_notifier = RequestsNotifier(TARGET_TELEGRAM_USER_ID, bot_users_repository, bot)


@bot.message_handler(commands=['start'])
@validate_user
def start_handler(message):
    try:
        bot.send_sticker(message.chat.id, StickerIds.hello)
        bot.send_message(message.chat.id, 'Вас приветствует Томочка Лапочка!\n\n'
                        '/top - получить несколько первых постов\n\n'
                        '/notifications - подписка на рассылку новых постов\n\n'
                        '/random - показать случайный пост')

        full_name, username = UserNamesExtractor.get_fullname_and_username(message.chat)
        bot_users_repository.ensure(BotUser(message.chat.id, full_name, username, True))
    finally:
        requests_notifier.notify(message.chat.id, '/start')
        logs_repository.add({'source': 'User message', 'from_id': message.chat.id, 'command': message.text, 'time': datetime.utcnow()})


@bot.message_handler(commands=['top'])
@validate_user
def handle_top_command(message):
    try:
        markup = types.InlineKeyboardMarkup(row_width=2)
        top1 = types.InlineKeyboardButton('Top 1', callback_data='top1')
        top3 = types.InlineKeyboardButton('Top 3', callback_data='top3')
        top5 = types.InlineKeyboardButton('Top 5', callback_data='top5')
        top10 = types.InlineKeyboardButton('Top 10', callback_data='top10')
        cancel = types.InlineKeyboardButton('Отмена', callback_data='topcancel')
        markup.add(top1, top3, top5, top10, cancel)
        bot.send_message(message.chat.id, 'Сколько последних постов показать??', reply_markup=markup)
    finally:
        requests_notifier.notify(message.chat.id, '/top')


@bot.callback_query_handler(lambda query: query.data in ['top1', 'top3', 'top5', 'top10', 'topcancel'])
def process_top_command_callback(query):
    try:
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

        log = {'source': 'User message', 'from_id': query.message.chat.id, 'command': query.data, 'result': 'successfully', 'time': datetime.utcnow()}
        bot.send_message(query.message.chat.id, f'Top {count} записей:')

        try:
            parser = SiteParser(URL_FEED)
            questions = parser.parse(count)
        except:
            bot.send_message(query.message.chat.id,
                            f'К сожалению, что-то сгнило! Попробуйте еще раз позже или посетите сайт царицы {URL_FEED}.')
            bot.send_sticker(query.message.chat.id, StickerIds.no_mood)
            log['result'] = 'parsing failed'
            return

        question_sender = QuestionSender(bot)
        question_sender.send_many(query.message.chat.id, questions)
    finally:
        requests_notifier.notify(query.message.chat.id, query.data)
        logs_repository.add(log)


@bot.message_handler(commands=['notifications'])
@validate_user
def handle_subscribe_command(message):
    try:
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
    finally:
        requests_notifier.notify(message.chat.id, '/notifications')


@bot.callback_query_handler(lambda query: query.data in ['subscribe', 'unsubscribe', 'subscribe_cancel'])
def process_subscribe_command_callback(query):
    try:
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
        bot.send_sticker(query.message.chat.id, StickerIds.done)
    finally:
        requests_notifier.notify(query.message.chat.id, query.data)
        logs_repository.add({'source': 'User message', 'from_id': query.message.chat.id, 'command': query.data, 'time': datetime.utcnow()})


@bot.message_handler(commands=['random'])
@validate_user
def handle_random_command(message):
    try:
        question = posts_archive_repository.get_random()
        question_sender = QuestionSender(bot)
        question_sender.send(message.chat.id, question)
    finally:
        requests_notifier.notify(message.chat.id, '/random')
        logs_repository.add({'source': 'User message', 'from_id': message.chat.id, 'command': message.text, 'time': datetime.utcnow()})


@bot.message_handler(commands=['online'])
@validate_user
def handle_online_command(message):
    try:
        time_utc_to = datetime.utcnow()
        time_utc_from = time_utc_to - timedelta(days=1)
        plot_sender = VkStatusPlotSender(
            bot,
            VkStatusPlotBuilder(vk_online_status_repository)
        )
        plot_sender.send(time_utc_from, time_utc_to, message.chat.id)
    finally:
        requests_notifier.notify(message.chat.id, '/online')


@bot.message_handler(content_types=['text'])
@validate_user
def handle_text(message):
    try:
        parsing_result = IncomingMessageParser.parse(message.text)

        if parsing_result.type == MessageType.UnsupportedCommand:
            bot.send_message(message.chat.id, 'Неподдерживаемая команда!!')
            bot.send_sticker(message.chat.id, StickerIds.loh)
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
                time_left = DatetimeUtils.timedelta_to_string(parsing_result.planned_time - (datetime.utcnow() + timedelta(hours=3)), '{days}д {hours}ч {minutes}м')
                text = f'Подтвердите, что хотите запланировать вопрос на {parsing_result.planned_time_str} (осталось {time_left}):\n\n' + parsing_result.question
                bot.send_message(message.chat.id, text, reply_markup=markup)
            else:
                bot.send_message(message.chat.id, parsing_result.comment)
            return

        if parsing_result.type == MessageType.VkStatusRequest:
            if parsing_result.is_valid:
                plot_sender = VkStatusPlotSender(
                    bot,
                    VkStatusPlotBuilder(vk_online_status_repository)
                )
                plot_sender.send(parsing_result.time_utc_from, parsing_result.time_utc_to, message.chat.id)
            else:
                bot.send_message(message.chat.id, parsing_result.comment)
            return
    finally:
        requests_notifier.notify(message.chat.id, message.text)
        logs_repository.add({'source': 'User message', 'from_id': message.chat.id, 'text': message.text, 'time': datetime.utcnow()})


@bot.callback_query_handler(lambda query: query.data in ['instant_question', 'scheduled_question', 'instant_cancel', 'scheduled_cancel'])
def process_ask_question_callback(query):
    try:
        if query.data in ['instant_cancel', 'scheduled_cancel']:
            bot.delete_message(query.message.chat.id, query.message.message_id)
            return

        edited_text = 'Спрашиваем...' if query.data == 'instant_question' else 'Планируем...'
        bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=edited_text)
        message_parts = query.message.text.split('\n', maxsplit=1)
        text = message_parts[1].strip()
        full_name, username = UserNamesExtractor.get_fullname_and_username(query.message.chat)
        added_by_name = full_name if full_name else (username if username else query.message.chat.id)
        now = datetime.utcnow()

        if query.data == 'instant_question':
            try:
                QuestionAsker.ask(text)
                questions_queue_repository.add(
                    QuestionQueueItem(
                        text=text,
                        time_created=now,
                        time_planned=now,
                        time_sent=now,
                        status=QuestionQueueItemStatus.InstantlyInserted,
                        added_by_id=query.message.chat.id,
                        added_by_name=added_by_name,
                        has_answer=False
                    )
                )
            except:
                bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id,
                                    text='К сожалению, что-то сгнило!')
        else:
            regex = re.compile(r'^.+(?P<datetime>\d\d\.\d\d\.\d\d\d\d\s+\d\d\:\d\d).+$')
            match = regex.match(message_parts[0])
            planned_time = DatetimeUtils.parse_dmy_hm(match.group('datetime'), timedelta(hours=-3))
            questions_queue_repository.add(
                QuestionQueueItem(
                    text=text,
                    time_created=now,
                    time_planned=planned_time,
                    time_sent=None,
                    status=QuestionQueueItemStatus.Unprocessed,
                    added_by_id=query.message.chat.id,
                    added_by_name=added_by_name,
                    has_answer=False
                )
            )

        bot.delete_message(query.message.chat.id, query.message.message_id)
        bot.send_sticker(query.message.chat.id, StickerIds.done)
    finally:
        requests_notifier.notify(query.message.chat.id, query.data)


@bot.message_handler(content_types=['sticker'])
@validate_user
def handle_sticker(message):
    try:
        bot.send_sticker(message.chat.id, StickerIds.rachal)
    finally:
        requests_notifier.notify(message.chat.id, 'send sticker to bot')
