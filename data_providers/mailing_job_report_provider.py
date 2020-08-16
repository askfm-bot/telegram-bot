from datetime import datetime, timedelta
from repositories import PostsArchiveRepository


class ReportData():
    def __init__(self, time, all_period, last_year, last_3month, last_month, last_week, last_day):
        self.time = time
        self.all_period = all_period
        self.last_year = last_year
        self.last_3month = last_3month
        self.last_month = last_month
        self.last_week = last_week
        self.last_day = last_day


def get():
    repository = PostsArchiveRepository()
    questions = repository.get_all()

    def ceil_dt(dt):
        return dt + (datetime.min - dt) % timedelta(minutes=30) + timedelta(hours=3)
    
    result = { 'Total':  ReportData('Total', 0, 0, 0, 0, 0, 0)}
    now = datetime.utcnow()

    for question in questions:
        key = ceil_dt(question.time).strftime('%H:%M')

        if key not in result.keys():
            result[key] = ReportData(key, 0, 0, 0, 0, 0, 0)
        
        diff_in_seconds = abs(now - question.time).total_seconds()

        result[key].all_period += 1
        result['Total'].all_period += 1

        if diff_in_seconds <= 365 * 24 * 60 * 60:
             result[key].last_year += 1
             result['Total'].last_year += 1

        if diff_in_seconds <= 90 * 24 * 60 * 60:
             result[key].last_3month += 1
             result['Total'].last_3month += 1

        if diff_in_seconds <= 30 * 24 * 60 * 60:
             result[key].last_month += 1
             result['Total'].last_month += 1

        if diff_in_seconds <= 7 * 24 * 60 * 60:
             result[key].last_week += 1
             result['Total'].last_week += 1

        if diff_in_seconds <= 24 * 60 * 60:
            result[key].last_day += 1
            result['Total'].last_day += 1

    sorted_result = [v for k, v in sorted(result.items())]

    return sorted_result