from datetime import datetime, timedelta
from repositories import QuestionQueueRepository, QuestionQueueItemStatus
import tools.question_asker as question_asker


def process():
    repository = QuestionQueueRepository()

    utc_now = datetime.utcnow()
    unprocessed_questions = [q for q in repository.get_unprocessed() if q.time_planned <= utc_now]
    
    for question in unprocessed_questions:
        repository.update(question.id, QuestionQueueItemStatus.InProgress, None)

    allowed_time_delta = timedelta(minutes=30)

    for question in unprocessed_questions:
        if question.time_planned < utc_now - allowed_time_delta:
            status = QuestionQueueItemStatus.Error
        else:
            try:
                question_asker.ask(question.text)
                status = QuestionQueueItemStatus.Processed
            except:
                status = QuestionQueueItemStatus.Error

        repository.update(question.id, status, utc_now)


if __name__ == "__main__":
    process()
