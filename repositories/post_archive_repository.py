from typing import List
from datetime import datetime
from pymongo import MongoClient
from models.question import Question
from config import CONNECTION_STRING


class PostsArchiveRepository:
    def __init__(self):
        client = MongoClient(CONNECTION_STRING)
        self.__archive = client.main.posts_archive

    @staticmethod
    def __build_question(post):
        if not post:
            return None
        return Question(
            title=post['title'],
            time=post['time'],
            time_relative=None,
            who_asked=post['who_asked'],
            answer=post['answer'],
            image_url=post['image_url']
        )

    @staticmethod
    def __map(posts):
        return list(map(lambda post: PostsArchiveRepository.__build_question(post), posts))

    def add_one(self, question: Question) -> None:
        try:
            self.__archive.insert_one({
                'title': question.title,
                'time': question.time,
                'who_asked': question.who_asked,
                'answer': question.answer,
                'image_url': question.image_url
            })
        except:
            pass

    def add_many(self, questions: List[Question]) -> None:
        for question in questions:
            self.add_one(question)

    def get_random(self) -> Question:
        posts = self.__archive.aggregate([{'$sample': {'size': 1}}])
        post = list(posts)[0]
        return PostsArchiveRepository.__build_question(post)

    def get_all(self) -> List[Question]:
        posts = self.__archive.find({})
        return PostsArchiveRepository.__map(posts)

    def get_from_interval(self, from_utc: datetime, to_utc: datetime) -> List[Question]:
        posts = self.__archive.find({'time': {'$lt': to_utc, '$gte': from_utc}})
        return PostsArchiveRepository.__map(posts)
