from datetime import datetime
from pymongo import MongoClient
from config import CONNECTION_STRING


class LastPostsRepository:
    def __init__(self):
        client = MongoClient(CONNECTION_STRING)
        self.__posts = client.main.last_posts

    def get_last_post_time(self) -> datetime:
        record = self.__posts.find_one({'_id': 0})
        return record['time']

    def update_last_post_time(self, time: datetime) -> None:
        self.__posts.update({'_id': 0}, {'$set': {'time': time}})
