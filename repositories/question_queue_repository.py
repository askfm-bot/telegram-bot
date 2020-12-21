from datetime import datetime
from typing import List, Optional
from bson.objectid import ObjectId
import pymongo
from models.question_queue_item import QuestionQueueItem, QuestionQueueItemStatus
from config import CONNECTION_STRING


class QuestionQueueRepository:
    def __init__(self):
        client = pymongo.MongoClient(CONNECTION_STRING)
        self.__queue = client.main.questions_queue

    @staticmethod
    def __build_question_queue_item(item):
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

    @staticmethod
    def __map(items):
        return list(map(lambda item: QuestionQueueRepository.__build_question_queue_item(item), items))

    def add(self, question_queue_item: QuestionQueueItem) -> None:
        self.__queue.insert_one({
            'text': question_queue_item.text,
            'time_created': question_queue_item.time_created,
            'time_planned': question_queue_item.time_planned,
            'time_sended': question_queue_item.time_sent,
            'status': int(question_queue_item.status),
            'added_by_id': question_queue_item.added_by_id,
            'added_by_name': question_queue_item.added_by_name,
            'has_answer': question_queue_item.has_answer
        })

    def get_by_id(self, id) -> QuestionQueueItem:
        return QuestionQueueRepository.__build_question_queue_item(self.__queue.find_one({'_id': ObjectId(id)}))

    def delete_by_id(self, id) -> None:
        self.__queue.delete_one({'_id': ObjectId(id)})

    def get_unprocessed(self) -> List[QuestionQueueItem]:
        return QuestionQueueRepository.__map(self.__queue.find({'status': int(QuestionQueueItemStatus.Unprocessed)}))

    def get_unanswered(self) -> List[QuestionQueueItem]:
        return QuestionQueueRepository.__map(self.__queue.find({'status': {'$in': [int(QuestionQueueItemStatus.Processed), int(QuestionQueueItemStatus.InstantlyInserted)]}, 'has_answer': False}))

    def get_top_by_status(self, status: QuestionQueueItemStatus, limit: int) -> List[QuestionQueueItem]:
        return QuestionQueueRepository.__map(
            self.__queue.find({'status': int(status)}).sort('time_planned', pymongo.DESCENDING).limit(limit))

    def update(self, id, status: QuestionQueueItemStatus, time_sent: Optional[datetime]) -> None:
        self.__queue.update_one({'_id': id}, {'$set': {'status': int(status), 'time_sended': time_sent}})

    def mark_as_answered(self, text: str) -> None:
        self.__queue.update_one({'$and': [{'text': text}, {'status': {
            '$in': [int(QuestionQueueItemStatus.Processed), int(QuestionQueueItemStatus.InstantlyInserted)]}}]},
                              {'$set': {'has_answer': True}})

    def add_additional_data(self, id, data: str) -> None:
        self.__queue.update_one({'_id': id}, {'$set': {'additional_data': data}})
