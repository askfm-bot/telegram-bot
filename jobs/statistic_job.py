import time
import random
import emoji
from datetime import datetime, timedelta
from bot import bot
from repositories import BotUsersRepository, PostsArchiveRepository


class Statistic:
    total_post_count = 0
    post_count_by_day_of_week = [0] * 7


day_of_week_str = {
    0: 'Пн',
    1: 'Вт',
    2: 'Ср',
    3: 'Чт',
    4: 'Пт',
    5: 'Сб',
    6: 'Вс'
}


def get_summary_message(question_count, week_start_str, week_end_str):
    part1 = random.choice(['она', 'эта', 'Лапочка', 'Lapochka', 'порно гёрл', 'попьюлар гёрл', 'Мерлин Монро', 'богема'])

    part2 = random.choice(['снизошла', 'удосужилась', 'умудрилась', 'решила', 'соизволила', 'не постеснялась', 'нашла время, чтобы', \
        'посчитала нужным', 'отвлеклась от важной работы, чтобы', 'выкроила минутку в своём плотном расписании, чтобы', 'улучила минутку, чтобы'])

    if (question_count % 10 == 1) and (question_count % 100 != 11):
        part3 = 'вопрос'
    elif (question_count % 10 in [2, 3, 4]) and (question_count % 100 not in [12, 13, 14]):
        part3 = 'вопроса'
    else:
        part3 = 'вопросов'
 
    return f'За последнюю неделю ({week_start_str} – {week_end_str}) {part1} {part2} ответить на {question_count} {part3}!'


def datetime_to_string(value):
    return value.strftime('%d.%m.%Y')


def statistic_to_string(statistic, week_start_utc, week_end_utc):
    result = emoji.emojize(':fire: СТАТИСТИКА :fire:\n\n', use_aliases=True)
    result += get_summary_message(statistic.total_post_count, datetime_to_string(week_start_utc), datetime_to_string(week_end_utc))
    result += '\n\n'
    for day_of_week in range(7):
        result += f'{day_of_week_str[day_of_week]}: {statistic.post_count_by_day_of_week[day_of_week]}\n'
    return result


def get_week_utc_range(utc_now):
    truncated_now =  datetime(utc_now.year, utc_now.month, utc_now.day)
    start = truncated_now - timedelta(days=truncated_now.weekday())
    end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start, end


def get_statistic(from_utc, to_utc, time_shift):
    repository = PostsArchiveRepository()
    posts = [post for post in repository.get_all() if from_utc - time_shift <= post.time <= to_utc - time_shift]
    statistic = Statistic()
    statistic.total_post_count = len(posts)
    for post in posts:
        statistic.post_count_by_day_of_week[(post.time + time_shift).weekday()] += 1
    return statistic


def main():
    utc_now = datetime.utcnow()

    # This is because Job Manager allows us to run the job only once a day
    # We want to run this job every Sunday at 21:00 UTC (every Monday 00:00 UTC+3)
    if utc_now.weekday() != 6:
        return

    time.sleep(500)

    utc_week_start, utc_week_end = get_week_utc_range(utc_now)
    time_shift = timedelta(hours=3)

    statistic = get_statistic(utc_week_start, utc_week_end, time_shift)
    
    bot_user_repository = BotUsersRepository()
    for user in bot_user_repository.get_subscribed_to_notifications():
        message = statistic_to_string(statistic, utc_week_start, utc_week_end)
        try:
            bot.send_message(user.id, message)
        except:
            bot_user_repository.delete(user.id)
        time.sleep(10)


if __name__ == '__main__':
   main()