from typing import Optional
from datetime import datetime, timedelta


class DatetimeUtils:
    @staticmethod
    def to_ddmmyyyy_hhmm(value: datetime, shift: Optional[timedelta] = None) -> str:
        if shift:
            value = value + shift
        return value.strftime('%d.%m.%Y %H:%M')
    
    @staticmethod
    def to_ddmmyyyy(value: datetime, shift: Optional[timedelta] = None) -> str:
        if shift:
            value = value + shift
        return value.strftime('%d.%m.%Y')

    @staticmethod
    def parse_dmy_hm(value: str, shift: Optional[timedelta] = None) -> datetime:
        result = datetime.strptime(value, '%d.%m.%Y %H:%M')
        if shift:
            result = result + shift
        return result

    @staticmethod
    def timedelta_to_string(tdelta: timedelta, fmt: str) -> str:
        if tdelta < timedelta(0):
            d = {'days': 0, 'hours': 0, 'minutes': 0}
        else:
            d = {'days': tdelta.days}
            d['hours'], rem = divmod(tdelta.seconds, 3600)
            d['minutes'], d['seconds'] = divmod(rem, 60)
        return fmt.format(**d)
