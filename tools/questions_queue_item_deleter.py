from repositories.question_queue_repository import QuestionQueueRepository
from models.question_queue_item import QuestionQueueItemStatus


class QuestionQueueItemDeleter:
    def __init__(self, repository: QuestionQueueRepository):
        self.__repository = repository

    def delete(self, question_id) -> bool:
        question = self.__repository.get_by_id(question_id)

        if (not question) or (question.status != QuestionQueueItemStatus.Unprocessed):
            return False

        self.__repository.delete_by_id(question_id)
        return True
