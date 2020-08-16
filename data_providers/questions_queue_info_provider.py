from datetime import datetime, timedelta
from repositories import QuestionQueueRepository


class QuestionsQueueInfo:
    def __init__(self, unprocessed_list, sended_list, error_list):
        self.unprocessed_list = unprocessed_list
        self.sended_list = sended_list
        self.error_list = error_list

    @staticmethod
    def format_datetime(datetime):
        return (datetime + timedelta(hours=3)).strftime('%d.%m.%Y %H:%M')


class UnprocessedQuestion:
    @staticmethod
    def map(question_queue_item):
        def strfdelta(tdelta, fmt):
            if tdelta < timedelta(0):
                d = {"days": 0, "hours": 0, "minutes": 0}
            else:
                d = {"days": tdelta.days}
                d["hours"], rem = divmod(tdelta.seconds, 3600)
                d["minutes"], d["seconds"] = divmod(rem, 60)
            return fmt.format(**d)

        item = UnprocessedQuestion()
        item.id = question_queue_item.id
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.scheduled_time = QuestionsQueueInfo.format_datetime(question_queue_item.time_planned)
        item.time_left = strfdelta(question_queue_item.time_planned - datetime.utcnow(), '{days}d {hours}h {minutes}m')
        return item


class ProcessedQuestion:
    @staticmethod
    def map(question_queue_item):
        item = ProcessedQuestion()
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.sent_time = QuestionsQueueInfo.format_datetime(question_queue_item.time_sended)
        item.has_answer = question_queue_item.has_answer
        return item


class ErrorMessage:
    @staticmethod
    def map(question_queue_item):
        item = ErrorMessage()
        item.question = question_queue_item.text
        item.author = question_queue_item.added_by_name
        item.scheduled_time = QuestionsQueueInfo.format_datetime(question_queue_item.time_planned)
        return item


def get():
    question_queue_repository = QuestionQueueRepository()
    unprocessed_list = question_queue_repository.get_unprocessed()
    unprocessed_list.sort(key=lambda x: x.time_planned, reverse=False)
    error_list = question_queue_repository.get_top_by_status(status=3, limit=20)
    processed_list = question_queue_repository.get_top_by_status(status=1, limit=50)
    manual_sended_list = question_queue_repository.get_top_by_status(status=4, limit=50)
    sended_list = [*processed_list, *manual_sended_list]
    sended_list.sort(key=lambda x: x.time_sended, reverse=True)
    return QuestionsQueueInfo(
        unprocessed_list=list(map(lambda item: UnprocessedQuestion.map(item), unprocessed_list)),
        sended_list=list(map(lambda item: ProcessedQuestion.map(item), sended_list)),
        error_list=list(map(lambda item: ErrorMessage.map(item), error_list))
    )
