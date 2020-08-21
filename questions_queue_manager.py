from repositories import QuestionQueueRepository, QuestionQueueItemStatus


def delete(question_id):
    repository = QuestionQueueRepository()
    question = repository.get_by_id(question_id)

    if (not question) or (question.status != QuestionQueueItemStatus.Unprocessed):
        return False

    repository.delete_by_id(question_id)
    return True