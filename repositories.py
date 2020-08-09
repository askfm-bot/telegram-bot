import pymongo
from pymongo import MongoClient
from config import CONNECTION_STRING
from models import Question


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


class PostsArchiveRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.archive = client.main.posts_archive

    def add_one(self, question):
        self.archive.insert_one({
            'title': question.title,
            'time': question.time,
            'who_asked': question.who_asked,
            'answer': question.answer
        })

    def add_many(self, questions):
        for question in questions:
            self.add_one(question)

    def get_random(self):
        posts = self.archive.aggregate([{ '$sample': { 'size': 1 } }])
        post = list(posts)[0]
        return Question(post['title'], post['time'], None, post['who_asked'], post['answer'])


class LogsRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.logs = client.main.logs

    def add(self, collection):
        self.logs.insert_one(collection)