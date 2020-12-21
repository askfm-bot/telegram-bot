from io import BytesIO
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from repositories.vk_user_online_statuses_repository import VkUserOnlineStatusesRepository
from tools.datetime_utils import DatetimeUtils


class VkStatusPlotBuilder:
    def __init__(self, repository: VkUserOnlineStatusesRepository):
        self.__repository = repository

    def build(self, time_utc_from: datetime, time_utc_to: datetime) -> BytesIO:
        def shift_time(time: datetime) -> datetime:
            return time + timedelta(hours=3)

        statuses = self.__repository.get(time_utc_from, time_utc_to)

        time_local_from = shift_time(time_utc_from)
        time_local_to = shift_time(time_utc_to)

        plt.figure(figsize=(12, 3.5))
        plt.xlim(time_local_from, time_local_to)
        plt.ylim(0, 2)
        plt.yticks([])

        def get_interval():
            diff = time_utc_to - time_utc_from
            hours = int(diff.total_seconds() // (60 * 60))
            if hours <= 36:
                return 1
            return int(round(hours / 24))

        x_axis_hours = mdates.HourLocator(interval=get_interval())
        plt.gca().xaxis.set_major_locator(x_axis_hours)
        x_axis_format = mdates.DateFormatter('%d.%m %H:%M')
        plt.gca().xaxis.set_major_formatter(x_axis_format)

        def get_x(condition):
            return [shift_time(status.time_utc) for status in statuses if condition(status)]

        x_mobile = get_x(lambda status: status.is_mobile)
        x_desktop = get_x(lambda status: not status.is_mobile)

        def stem(x, marker_color, label_prefix):
            count = len(x)
            y = [1] * count
            markerline, stemlines, _ = plt.stem(x, y, linefmt='k:', markerfmt=f'{marker_color}o', basefmt=' ', label=f'{label_prefix} ({count})')
            plt.setp(stemlines, linewidth=0.8)
            plt.setp(markerline, markersize=4.5)

        if x_mobile:
            stem(x_mobile, 'g', 'Mobile')

        if x_desktop:
            stem(x_desktop, 'b', 'Desktop')

        def build_title():
            def time_to_str(time):
                return DatetimeUtils.to_ddmmyyyy_hhmm(time)
            return time_to_str(time_local_from) + ' – ' + time_to_str(time_local_to)

        plt.legend()
        plt.title(build_title())
        plt.gcf().autofmt_xdate()

        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        plt.close()
        buffer.seek(0)

        return buffer
