from datetime import datetime, timedelta
from repositories.post_archive_repository import PostsArchiveRepository


class QuestionCountReportData:
    def __init__(self, all_period: int, last_year: int, last_3_months: int, 
                 last_month: int, last_week: int, last_day: int):
        self.all_period = all_period
        self.last_year = last_year
        self.last_3_months = last_3_months
        self.last_month = last_month
        self.last_week = last_week
        self.last_day = last_day


class QuestionCountReportProvider:
    def __init__(self, repository: PostsArchiveRepository):
        self.__repository = repository

    def get(self):
        questions = self.__repository.get_all()
        result = QuestionCountReportData(0, 0, 0, 0, 0, 0)
        now = datetime.utcnow()

        for question in questions:
            diff_in_seconds = abs(now - question.time).total_seconds()

            result.all_period += 1

            if diff_in_seconds <= 365 * 24 * 60 * 60:
                result.last_year += 1

            if diff_in_seconds <= 90 * 24 * 60 * 60:
                result.last_3_months += 1

            if diff_in_seconds <= 30 * 24 * 60 * 60:
                result.last_month += 1

            if diff_in_seconds <= 7 * 24 * 60 * 60:
                result.last_week += 1

            if diff_in_seconds <= 24 * 60 * 60:
                result.last_day += 1

        return result
