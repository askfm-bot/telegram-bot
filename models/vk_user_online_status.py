from datetime import datetime


class VkUserOnlineStatus:
    def __init__(self, time_utc: datetime, is_mobile: bool):
        self.time_utc = time_utc
        self.is_mobile = is_mobile
