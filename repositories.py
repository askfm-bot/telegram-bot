import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from config import CONNECTION_STRING
from models import BotUser, Question, QuestionQueueItem, QuestionQueueItemStatus


class BotUsersRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.users = client.main.bot_users

    def __build_user(self, user):
        if not user:
            return None

        return BotUser(
            user['id'],
            user['full_name'],
            user['username'],
            user['is_subscribed_to_notifications']
        )

    def __map(self, users):
        return list(map(lambda user: self.__build_user(user), users))

    def get_all(self):
        return self.__map(self.users.find({}))

    def get_subscribed_to_notifications(self):
        return self.__map(self.users.find({ 'is_subscribed_to_notifications': True }))

    def get_by_id(self, user_id):
        return self.__build_user(self.users.find_one({ 'id': user_id }))

    def update_is_subscribed(self, user_id, is_subscribed):
        self.users.update( { 'id': user_id }, { '$set': { 'is_subscribed_to_notifications': is_subscribed } })

    def delete(self, user_id):
        self.users.delete_many({ 'id': user_id })

    def ensure(self, user):
        self.delete(user.id)
        self.users.insert_one({
            'id': user.id,
            'full_name': user.full_name,
            'username': user.username,
            'is_subscribed_to_notifications': user.is_subscribed_to_notifications
        })


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
        try:
            self.archive.insert_one({
                'title': question.title,
                'time': question.time,
                'who_asked': question.who_asked,
                'answer': question.answer,
                'image_url': question.image_url
            })
        except:
            pass

    def add_many(self, questions):
        for question in questions:
            self.add_one(question)

    def get_random(self):
        posts = self.archive.aggregate([{ '$sample': { 'size': 1 } }])
        post = list(posts)[0]
        return Question(post['title'], post['time'], None, post['who_asked'], post['answer'], post['image_url'])

    def get_all(self):
        posts = self.archive.find({})
        return list(map(lambda post: Question(post['title'], post['time'], None, post['who_asked'], post['answer'], post['image_url']), posts))


class QuestionQueueRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.queue = client.main.questions_queue

    def __build_question_queue_item(self, item):
        if not item:
            return None

        result = QuestionQueueItem(
            item['text'],
            item['time_created'],
            item['time_planned'],
            item['time_sended'],
            QuestionQueueItemStatus(item['status']),
            item['added_by_id'],
            item['added_by_name'],
            item['has_answer']
        )
        result.id = item['_id']
        return result

    def __map(self, items):
        return list(map(lambda item: self.__build_question_queue_item(item), items))

    def add(self, question_queue_item):
        self.queue.insert_one({
            'text': question_queue_item.text,
            'time_created': question_queue_item.time_created,
            'time_planned': question_queue_item.time_planned,
            'time_sended': question_queue_item.time_sended,
            'status': int(question_queue_item.status),
            'added_by_id': question_queue_item.added_by_id,
            'added_by_name': question_queue_item.added_by_name,
            'has_answer': question_queue_item.has_answer
        })

    def get_by_id(self, id):
        return self.__build_question_queue_item(self.queue.find_one({ '_id': ObjectId(id) }))

    def delete_by_id(self, id):
        self.queue.delete_one({ '_id': ObjectId(id) })

    def get_unprocessed(self):
        return self.__map(self.queue.find({ 'status': int(QuestionQueueItemStatus.Unprocessed) }))

    def get_top_by_status(self, status, limit):
        return self.__map(self.queue.find({ 'status': int(status) }).sort('time_planned', pymongo.DESCENDING).limit(limit))

    def update(self, id, status, time_sended):
        self.queue.update_one({'_id': id }, { '$set': { 'status': int(status), 'time_sended': time_sended } })

    def mark_as_answered(self, text):
        self.queue.update_one({ '$and': [{'text': text }, { 'status': { '$in': [int(QuestionQueueItemStatus.Processed), int(QuestionQueueItemStatus.InstantlyInserted)] } }] }, { '$set': { 'has_answer': True } })

    def add_additional_data(self, id, data):
        self.queue.update_one({ '_id': id }, { '$set': { 'additional_data': data } })


class LogsRepository():
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.logs = client.main.logs

    def add(self, collection):
        self.logs.insert_one(collection)