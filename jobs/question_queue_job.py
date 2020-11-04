import traceback
from datetime import datetime, timedelta
from repositories import QuestionQueueRepository, QuestionQueueItemStatus
from tools.question_asker import QuestionAsker


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
                QuestionAsker.ask(question.text)
                status = QuestionQueueItemStatus.Processed
            except Exception as ex:
                status = QuestionQueueItemStatus.Error
                error = ''.join(traceback.format_exception(etype=type(ex), value=ex, tb=ex.__traceback__))
                repository.add_additional_data(question.id, error)

        repository.update(question.id, status, utc_now)


if __name__ == "__main__":
    process()
