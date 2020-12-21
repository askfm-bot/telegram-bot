import traceback
from datetime import datetime, timedelta
from repositories.question_queue_repository import QuestionQueueRepository
from models.question_queue_item import QuestionQueueItemStatus
from tools.question_asker import QuestionAsker


class QuestionQueueHandler:
    def __init__(self, repository: QuestionQueueRepository):
        self.__repository = repository

    def process(self) -> None:
        utc_now = datetime.utcnow()
        unprocessed_questions = [q for q in self.__repository.get_unprocessed() if q.time_planned <= utc_now]

        for question in unprocessed_questions:
            self.__repository.update(question.id, QuestionQueueItemStatus.InProgress, time_sent=None)

        allowed_time_delta = timedelta(minutes=30)

        for question in unprocessed_questions:
            if question.time_planned < utc_now - allowed_time_delta:
                status = QuestionQueueItemStatus.Error
            else:
                try:
                    QuestionAsker.ask(question.text)
                    status = QuestionQueueItemStatus.Processed
                except Exception as ex:
                    status = QuestionQueueItemStatus.Error
                    error = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
                    self.__repository.add_additional_data(question.id, error)

            self.__repository.update(question.id, status, utc_now)
