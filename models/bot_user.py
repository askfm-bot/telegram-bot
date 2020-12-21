class BotUser:
    def __init__(self, id, full_name: str, username: str, is_subscribed_to_notifications: bool):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.is_subscribed_to_notifications = is_subscribed_to_notifications
