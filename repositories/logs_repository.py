from pymongo import MongoClient
from config import CONNECTION_STRING


class LogsRepository:
    def __init__(self):
        client = MongoClient(CONNECTION_STRING)
        self.__logs = client.main.logs

    def add(self, collection):
        self.__logs.insert_one(collection)
