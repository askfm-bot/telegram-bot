import random
import time
from telebot import TeleBot
from static.strings import Strings
from repositories.bot_users_repository import BotUsersRepository


class RequestsNotifier:
    def __init__(self, target_user_id: int, bot_users_repository: BotUsersRepository, bot: TeleBot):
        self.__target_user_id = target_user_id
        self.__bot_users_repository = bot_users_repository
        self.__bot = bot

    @staticmethod
    def __build_text(message: str) -> str:
        name = Strings.capitalize(random.choice(Strings.she))
        return f'{name} запросила команду:\n{message}'

    def notify(self, requestor_user_id: int, message: str) -> None:
        if self.__target_user_id == requestor_user_id:
            users = self.__bot_users_repository.get_subscribed_to_notifications()
            for user in users:
                if user.id != self.__target_user_id:
                    try:
                        text = RequestsNotifier.__build_text(message)
                        self.__bot.send_message(user.id, text)
                        time.sleep(0.5)
                    except:
                        self.__bot_users_repository.update_is_subscribed(user.id, False)
