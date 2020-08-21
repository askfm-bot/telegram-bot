import time
import random
from datetime import datetime
from bot_handlers import bot
from repositories import BotUsersRepository, LastPostsRepository, PostsArchiveRepository, QuestionQueueRepository, LogsRepository
from tools.site_parser import get_questions
from shared.methods import send_question


def get_title_message(question_count):
    part1 = random.choice(['Она', 'Эта', 'Лапочка', 'Lapochka', 'Порно гёрл', 'Попьюлар гёрл', 'Мерлин Монро', 'Богема'])

    part2 = random.choice(['снизошла', 'удосужилась', 'умудрилась', 'решила', 'соизволила', 'не постеснялась', 'нашла время, чтобы', \
        'посчитала нужным', 'отвлеклась от важной работы, чтобы', 'выкроила минутку в своём плотном расписании, чтобы', 'улучила минутку, чтобы'])

    if (question_count % 10 == 1) and (question_count % 100 != 11):
        part3 = 'новый вопрос'
    elif (question_count % 10 in [2, 3, 4]) and (question_count % 100 not in [12, 13, 14]):
        part3 = 'новых вопроса'
    else:
        part3 = 'новых вопросов'
 
    return f'{part1} {part2} ответить на {question_count} {part3}:'


def send_notifications():
    logs_repository = LogsRepository()
    log = { 'source': 'Mailing Job', 'time': datetime.now() }

    try:
        questions = get_questions()
        log['parsing_result'] = 'successfully'
        log['parsed_questions_count'] = len(questions)
    except:
        log['parsing_result'] = 'failed'
        logs_repository.add(log)
        return

    last_posts_repository = LastPostsRepository()
    last_date = last_posts_repository.get_last_post_time()
    new_questions = [q for q in questions if q.time > last_date]

    log['extracted_last_date'] = last_date
    log['new_questions_count'] = len(new_questions)

    if not new_questions:
        logs_repository.add(log)
        return

    posts_archive_repository = PostsArchiveRepository()
    posts_archive_repository.add_many(new_questions)

    questions_queue_repository = QuestionQueueRepository()
    for question in new_questions:
        if question.title:
            questions_queue_repository.mark_as_answered(question.title.strip())

    last_posts_repository.update_last_post_time(new_questions[0].time)
    log['updated_last_date'] = new_questions[0].time

    bot_user_repository = BotUsersRepository()
    log['subscriber_ids'] = []
    log['removed_from_subscribers'] = []

    for user in bot_user_repository.get_subscribed_to_notifications():
        log['subscriber_ids'].append(user.id)
        sent_count = 0
        try:
            bot.send_message(user.id, get_title_message(len(new_questions)))
            sent_count += 1
            for question in new_questions:
                send_question(bot, user.id, question)
                sent_count += 1
        except:
            if sent_count == 0:
                bot_user_repository.delete(user.id)
                log['removed_from_subscribers'].append(user.id)
        time.sleep(10)

    logs_repository.add(log)


if __name__ == '__main__':
    send_notifications()