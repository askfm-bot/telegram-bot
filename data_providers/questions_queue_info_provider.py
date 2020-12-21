from datetime import datetime, timedelta
from repositories.question_queue_repository import QuestionQueueRepository
from models.question_queue_item import QuestionQueueItemStatus
from tools.datetime_utils import DatetimeUtils


class QuestionsQueueInfo:
    def __init__(self, unprocessed_list, sent_list, unanswered_list, error_list):
        self.unprocessed_list = unprocessed_list
        self.sent_list = sent_list
        self.error_list = error_list
        self.unanswered_list = unanswered_list


class UnprocessedQuestion:
    @staticmethod
    def map(question_queue_item):
        item = UnprocessedQuestion()
        item.id = question_queue_item.id
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.scheduled_time = DatetimeUtils.to_ddmmyyyy_hhmm(question_queue_item.time_planned, timedelta(hours=3))
        item.time_left = DatetimeUtils.timedelta_to_string(question_queue_item.time_planned - datetime.utcnow(), '{days}d {hours}h {minutes}m')
        return item


class ProcessedQuestion:
    @staticmethod
    def map(question_queue_item):
        item = ProcessedQuestion()
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.sent_time = DatetimeUtils.to_ddmmyyyy_hhmm(question_queue_item.time_sent, timedelta(hours=3))
        item.has_answer = question_queue_item.has_answer
        return item


class UnansweredQuestion:
    @staticmethod
    def map(question_queue_item):
        item = UnansweredQuestion()
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.sent_time = DatetimeUtils.to_ddmmyyyy_hhmm(question_queue_item.time_sent, timedelta(hours=3))
        return item


class ErrorMessage:
    @staticmethod
    def map(question_queue_item):
        item = ErrorMessage()
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.scheduled_time = DatetimeUtils.to_ddmmyyyy_hhmm(question_queue_item.time_planned, timedelta(hours=3))
        return item


class QuestionQueueInfoProvider:
    def __init__(self, repository: QuestionQueueRepository):
        self.__repository = repository

    def get(self) -> QuestionsQueueInfo:
        unprocessed_list = self.__repository.get_unprocessed()
        unprocessed_list.sort(key=lambda x: x.time_planned, reverse=False)
        error_list = self.__repository.get_top_by_status(QuestionQueueItemStatus.Error, limit=20)
        processed_list = self.__repository.get_top_by_status(QuestionQueueItemStatus.Processed, limit=50)
        manual_sent_list = self.__repository.get_top_by_status(QuestionQueueItemStatus.InstantlyInserted, limit=50)
        sent_list = [*processed_list, *manual_sent_list]
        sent_list.sort(key=lambda x: x.time_sent, reverse=True)
        unanswered_list = self.__repository.get_unanswered()
        unanswered_list.sort(key=lambda x: x.time_sent, reverse=True)

        def map(mapper, array):
            return [mapper(item) for item in array]

        return QuestionsQueueInfo(
            unprocessed_list=map(UnprocessedQuestion.map, unprocessed_list),
            sent_list=map(ProcessedQuestion.map, sent_list),
            unanswered_list=map(UnansweredQuestion.map, unanswered_list),
            error_list=map(ErrorMessage.map, error_list)
        )
