from datetime import datetime
from repositories.vk_user_online_statuses_repository import VkUserOnlineStatusesRepository
from models.vk_user_online_status import VkUserOnlineStatus
from tools.vk_user_status_provider import VkUserOnlineStatusProvider


class VkUserOnlineStatusCollector:
    def __init__(self, status_provider: VkUserOnlineStatusProvider, status_repository: VkUserOnlineStatusesRepository):
        self.__status_provider = status_provider
        self.__status_repository = status_repository

    def collect(self) -> None:
        status = self.__status_provider.get()

        self.__status_repository.add_if_not_exists(
            VkUserOnlineStatus(
                time_utc=status.last_seen_time_utc,
                is_mobile=status.last_seen_is_mobile
            )
        )

        if status.is_online_now:
            self.__status_repository.add_if_not_exists(
                VkUserOnlineStatus(
                    time_utc=datetime.utcnow(),
                    is_mobile=status.is_mobile_now
                )
            )
