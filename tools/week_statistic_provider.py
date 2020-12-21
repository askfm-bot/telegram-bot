from datetime import datetime, timedelta
from repositories.post_archive_repository import PostsArchiveRepository
from models.week_statistic import WeekStatistic


class WeekStatisticProvider:
    def __init__(self, time_shift: timedelta, post_archive_repository: PostsArchiveRepository):
        self.__time_shift = time_shift
        self.__post_archive_repository = post_archive_repository

    @staticmethod
    def __get_week_utc_range(any_date_of_week_utc: datetime):
        truncated_any_date_of_week_utc = datetime(any_date_of_week_utc.year, any_date_of_week_utc.month,any_date_of_week_utc.day)
        start = truncated_any_date_of_week_utc - timedelta(days=truncated_any_date_of_week_utc.weekday())
        end = start + timedelta(days=6, hours=23, minutes=59, seconds=59)
        return start, end

    def __extract(self, from_utc: datetime, to_utc: datetime, time_shift: timedelta) -> WeekStatistic:
        posts = self.__post_archive_repository.get_from_interval(from_utc - time_shift, to_utc - time_shift)
        statistic = WeekStatistic()
        statistic.week_start_utc = from_utc
        statistic.week_end_utc = to_utc
        statistic.total_post_count = len(posts)
        for post in posts:
            weekday = (post.time + time_shift).weekday()
            statistic.post_count_by_day_of_week[weekday] += 1
        return statistic

    def get(self, any_date_of_week_utc: datetime) -> WeekStatistic:
        utc_week_start, utc_week_end = WeekStatisticProvider.__get_week_utc_range(any_date_of_week_utc)
        return self.__extract(utc_week_start, utc_week_end, self.__time_shift)
