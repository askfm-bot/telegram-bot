from typing import List
from datetime import datetime
from pymongo import MongoClient
from models.vk_user_online_status import VkUserOnlineStatus
from config import CONNECTION_STRING


class VkUserOnlineStatusesRepository:
    def __init__(self):
        client = MongoClient(CONNECTION_STRING)
        self.__statuses = client.main.vk_user_online_statuses

    @staticmethod
    def __build_vk_user_online_status(vk_user_online_status):
        if not vk_user_online_status:
            return None

        return VkUserOnlineStatus(
            vk_user_online_status['time_utc'],
            vk_user_online_status['is_mobile']
        )

    @staticmethod
    def __map(vk_user_online_statuses):
        return list(map(lambda vk_user_online_status:VkUserOnlineStatusesRepository.__build_vk_user_online_status(
            vk_user_online_status), vk_user_online_statuses))

    def check_by_time(self, time_utc: datetime) -> bool:
        result = self.__statuses.find_one({'time_utc': time_utc})
        return True if result else False

    def add(self, vk_user_online_status: VkUserOnlineStatus) -> None:
        self.__statuses.insert_one({
            'time_utc': vk_user_online_status.time_utc,
            'is_mobile': vk_user_online_status.is_mobile
        })

    def add_if_not_exists(self, vk_user_online_status: VkUserOnlineStatus) -> bool:
        if not self.check_by_time(vk_user_online_status.time_utc):
            self.add(vk_user_online_status)
            return True
        return False

    def get(self, time_utc_from: datetime, time_utc_to: datetime) -> List[VkUserOnlineStatus]:
        result = self.__statuses.find({'time_utc': {'$lt': time_utc_to, '$gte': time_utc_from}}).sort('time_utc')
        return VkUserOnlineStatusesRepository.__map(result)
