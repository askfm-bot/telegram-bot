from typing import List
from pymongo import MongoClient
from models.bot_user import BotUser
from config import CONNECTION_STRING


class BotUsersRepository:
    def __init__(self):
        client = MongoClient(CONNECTION_STRING)
        self.__users = client.main.bot_users

    @staticmethod
    def __build_user(user):
        if not user:
            return None

        return BotUser(
            user['id'],
            user['full_name'],
            user['username'],
            user['is_subscribed_to_notifications']
        )

    @staticmethod
    def __map(users):
        return list(map(lambda user: BotUsersRepository.__build_user(user), users))

    def __delete(self, user_id: int) -> None:
        self.__users.delete_many({'id': user_id})

    def get_all(self) -> List[BotUser]:
        return BotUsersRepository.__map(self.__users.find({}))

    def get_subscribed_to_notifications(self) -> List[BotUser]:
        return BotUsersRepository.__map(self.__users.find({'is_subscribed_to_notifications': True}))

    def get_by_id(self, user_id: int) -> BotUser:
        return BotUsersRepository.__build_user(self.__users.find_one({'id': user_id}))

    def update_is_subscribed(self, user_id: int, is_subscribed: bool) -> None:
        self.__users.update({'id': user_id}, {'$set': {'is_subscribed_to_notifications': is_subscribed}})

    def ensure(self, user: BotUser) -> None:
        self.__delete(user.id)
        self.__users.insert_one({
            'id': user.id,
            'full_name': user.full_name,
            'username': user.username,
            'is_subscribed_to_notifications': user.is_subscribed_to_notifications
        })
