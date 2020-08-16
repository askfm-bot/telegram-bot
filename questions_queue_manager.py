from repositories import QuestionQueueRepository


def delete(question_id):
    repository = QuestionQueueRepository()
    question = repository.get_by_id(question_id)

    if (not question) or (question.status != 0):
        return False

    repository.delete_by_id(question_id)
    return True