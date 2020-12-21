import time
from datetime import datetime
import random
from typing import Dict
from telebot import TeleBot
from emoji import emojize
from models.week_statistic import WeekStatistic
from static.strings import Strings
from tools.week_statistic_provider import WeekStatisticProvider
from tools.datetime_utils import DatetimeUtils
from repositories.bot_users_repository import BotUsersRepository


class WeekStatisticNotifier:
    def __init__(self,
                 bot: TeleBot,
                 statistic_provider: WeekStatisticProvider,
                 bot_user_repository: BotUsersRepository):
        self.__bot = bot
        self.__statistic_provider = statistic_provider
        self.__bot_user_repository = bot_user_repository

    __day_of_week_str: Dict[int, str] = {
        0: 'Пн',
        1: 'Вт',
        2: 'Ср',
        3: 'Чт',
        4: 'Пт',
        5: 'Сб',
        6: 'Вс'
    }

    @staticmethod
    def __get_summary_message(question_count: int,
                              week_start_str: str,
                              week_end_str: str) -> str:
        part1 = random.choice(Strings.she)
        part2 = random.choice(Strings.found_time)
        part3 = Strings.question(question_count)
        return f'За последнюю неделю ({week_start_str} – {week_end_str}) {part1} {part2} ответить на {question_count} {part3}!'

    @staticmethod
    def __statistic_to_string(statistic: WeekStatistic) -> str:
        result = emojize(':fire: СТАТИСТИКА :fire:\n\n', use_aliases=True)
        result += WeekStatisticNotifier.__get_summary_message(
            statistic.total_post_count,
            DatetimeUtils.to_ddmmyyyy(statistic.week_start_utc),
            DatetimeUtils.to_ddmmyyyy(statistic.week_end_utc)
        )
        if statistic.total_post_count > 0:
            result += '\n\n'
            for day_of_week in range(7):
                result += f'{WeekStatisticNotifier.__day_of_week_str[day_of_week]}: {statistic.post_count_by_day_of_week[day_of_week]}\n'
        return result

    def notify(self, any_date_of_week: datetime) -> None:
        statistic = self.__statistic_provider.get(any_date_of_week)

        for user in self.__bot_user_repository.get_subscribed_to_notifications():
            message = WeekStatisticNotifier.__statistic_to_string(statistic)
            try:
                self.__bot.send_message(user.id, message)
            except:
                self.__bot_user_repository.update_is_subscribed(user.id, False)
            time.sleep(2)
