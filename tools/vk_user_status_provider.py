from datetime import datetime
import vk


class VkUserOnlineStatus:
    def __init__(self, is_online_now, is_mobile_now, last_seen_time_utc, last_seen_is_mobile):
        self.is_online_now = is_online_now
        self.is_mobile_now = is_mobile_now
        self.last_seen_time_utc = last_seen_time_utc
        self.last_seen_is_mobile = last_seen_is_mobile


class VkUserOnlineStatusProvider:
    def __init__(self, user_id: int, access_token: str):
        self.__user_id = user_id
        self.__access_token = access_token

    def get(self) -> VkUserOnlineStatus:
        session = vk.Session(access_token=self.__access_token)
        vk_api = vk.API(session)
        user = vk_api.users.get(user_id=self.__user_id, fields='online, last_seen', v='5.52')[0]

        last_seen = user['last_seen']
        last_seen_time_utc = datetime.utcfromtimestamp(last_seen['time'])
        last_seen_is_mobile = True if last_seen['platform'] != 7 else False
        is_online_now = True if user['online'] else False
        is_mobile_now = None
        if is_online_now:
            is_mobile_now = True if ('online_mobile' in user) and (user['online_mobile'] == 1) else False

        return VkUserOnlineStatus(is_online_now, is_mobile_now, last_seen_time_utc, last_seen_is_mobile)
