import re
from datetime import datetime, timedelta
from enum import Enum
from tools.datetime_utils import DatetimeUtils


class MessageType(Enum):
    UnsupportedCommand = 0
    ZakruzhilasCommand = 1
    InstantQuestion = 2
    ScheduledQuestion = 3
    VkStatusRequest = 4


class MessageParsingResult:
    pass


class IncomingMessageParser:
    @staticmethod
    def parse(text: str) -> MessageParsingResult:
        text = text.strip()
        result = MessageParsingResult()

        if text.startswith('-q'):
            pattern = re.compile(r'^-q\s+(?P<datetime>\d{1,2}\.\d{1,2}\.\d\d\d\d\s+\d{1,2}\:\d{1,2})(?P<text>[\s\S]+)$')
            match = pattern.match(text)
            if match:
                result.type = MessageType.ScheduledQuestion
                try:
                    planned_time = DatetimeUtils.parse_dmy_hm(match.group('datetime'))
                    planned_time_str = DatetimeUtils.to_ddmmyyyy_hhmm(planned_time)
                    now = datetime.utcnow() + timedelta(hours=3)
                    if planned_time < now:
                        result.is_valid = False
                        now_str = DatetimeUtils.to_ddmmyyyy_hhmm(now)
                        result.comment = f'Необходимо указать время из будущего! Время на сервере {now_str}, а вы ' \
                                         f'указали {planned_time_str}. '
                    else:
                        result.is_valid = True
                        result.planned_time = planned_time
                        result.planned_time_str = planned_time_str
                        result.question = match.group('text').strip()
                except:
                    result.is_valid = False
                    result.comment = 'Вы указали невалидную дату и/или время!'
            else:
                result.is_valid = True
                result.type = MessageType.InstantQuestion
                result.question = text[2:].strip()
            if result.is_valid:
                question_len = len(result.question)
                max_question_len = 300
                if question_len > max_question_len:
                    result.is_valid = False
                    result.comment = f'Максимальная длина вопроса - {max_question_len} символов. В вашем вопросе {question_len} символов. '
                if question_len <= 0:
                    result.is_valid = False
                    result.comment = 'Вопрос должен содержать хотя бы один символ.'
            return result

        if text.startswith('-vk'):
            result.type = MessageType.VkStatusRequest
            pattern = re.compile(r'^-vk\s+(?P<time_from>\d{1,2}\.\d{1,2}\.\d\d\d\d\s+\d{1,2}\:\d{1,2})\s+(?P<time_to>\d{1,2}\.\d{1,2}\.\d\d\d\d\s+\d{1,2}\:\d{1,2})$')
            match = pattern.match(text)
            result.is_valid = True
            if match:
                time_utc_from = DatetimeUtils.parse_dmy_hm(match.group('time_from'), timedelta(hours=-3))
                time_utc_to = DatetimeUtils.parse_dmy_hm(match.group('time_to'), timedelta(hours=-3))
                if (time_utc_from > time_utc_to):
                    time_utc_from, time_utc_to = time_utc_to, time_utc_from
                diff_in_hours = int((time_utc_to - time_utc_from).total_seconds() // (60 * 60))
                min_hours = 2
                max_hours = 7 * 24
                if min_hours <= diff_in_hours <= max_hours:
                    result.time_utc_from = time_utc_from
                    result.time_utc_to = time_utc_to
                else:
                    result.is_valid = False
                    result.comment = f'Длина интервала должна быть в диапозоне от {min_hours} до {max_hours} часов (вы запросили {diff_in_hours} часов).'
            else:
                result.is_valid = False
                result.comment = 'Не удалось распарсить запрос.'
            return result

        if any(word in text.lower() for word in ['закружился', 'закружилась', 'кружусь', 'кружимся', 'кружится']):
            result.type = MessageType.ZakruzhilasCommand
            return result

        result.type = MessageType.UnsupportedCommand
        return result
