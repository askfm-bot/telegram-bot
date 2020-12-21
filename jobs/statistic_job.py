import time
from datetime import datetime, timedelta
from bot import bot
from repositories.bot_users_repository import BotUsersRepository
from repositories.post_archive_repository import PostsArchiveRepository
from tools.week_statistic_notifier import WeekStatisticNotifier
from tools.week_statistic_provider import WeekStatisticProvider


def execute():
    utc_now = datetime.utcnow()

    # This is because Job Manager allows us to run the job only once a day
    # We want to run this job every Sunday at 21:00 UTC (every Monday 00:00 UTC+3)
    if utc_now.weekday() != 6:
        return

    time.sleep(500)

    notifier = WeekStatisticNotifier(
        bot,
        WeekStatisticProvider(
            timedelta(hours=3),
            PostsArchiveRepository()
        ),
        BotUsersRepository()
    )

    notifier.notify(utc_now)


if __name__ == '__main__':
    execute()
