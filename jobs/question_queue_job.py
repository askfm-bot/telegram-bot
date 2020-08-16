from datetime import datetime, timedelta
from repositories import QuestionQueueRepository
import tools.question_asker as question_asker


def process():
    repository = QuestionQueueRepository()

    utc_now = datetime.utcnow()
    unprocessed_questions = [q for q in repository.get_unprocessed() if q.time_planned <= utc_now]
    
    for question in unprocessed_questions:
        repository.update(question.id, 2, None)

    allowed_time_delta = timedelta(minutes=30)

    for question in unprocessed_questions:
        if question.time_planned < utc_now - allowed_time_delta:
            status = 3
        else:
            try:
                question_asker.ask(question.text)
                status = 1
            except:
                status = 3

        repository.update(question.id, status, utc_now)


if __name__ == "__main__":
    process()
