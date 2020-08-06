import pymongo
from pymongo import MongoClient
from config import CONNECTION_STRING


class SubscribersRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.subscribers = client.main.subscribers

    def is_user_exists(self, user_id):
        record = self.subscribers.find_one({ 'user_id': user_id })
        return True if record else False
    
    def get_all_users(self):
        return self.subscribers.find({})

    def ensure_user(self, user_id):
        record = self.subscribers.find_one({ 'user_id': user_id })
        if not record:
            self.subscribers.insert_one({ 'user_id': user_id })

    def delete_user(self, user_id):
        self.subscribers.delete_many({ 'user_id': user_id })


class LastPostsRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.posts = client.main.last_posts

    def get_last_post_time(self):
        record = self.posts.find_one({ '_id': 0 })
        return record['time']

    def update_last_post_time(self, time):
        self.posts.update({ '_id': 0 }, { '$set': { 'time': time } })


class LogsRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.logs = client.main.logs

    def add(self, collection):
        self.logs.insert_one(collection)