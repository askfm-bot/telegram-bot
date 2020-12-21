from datetime import datetime


class WeekStatistic:
    week_start_utc = datetime.utcnow()
    week_end_utc = datetime.utcnow()
    total_post_count = 0
    post_count_by_day_of_week = [0] * 7
