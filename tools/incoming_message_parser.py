
import re
from datetime import datetime, timedelta
from enum import Enum


class MessageType(Enum):
    UnsupportedCommand = 0
    ZakruzhilasCommand = 1
    InstantQuestion = 2
    ScheduledQuestion = 3


class MessageParsingResult:
    pass


def parse(text: str):
    text = text.strip()
    result = MessageParsingResult()

    if text.startswith('-q'):
        pattern = re.compile(r'^-q\s+(?P<datetime>\d\d\.\d\d\.\d\d\d\d\s+\d\d:\d\d)(?P<text>[\s\S]+)$')
        match = pattern.match(text)
        if match:
            result.type = MessageType.ScheduledQuestion
            try:
                planned_time = datetime.strptime(match.group('datetime'), '%d.%m.%Y %H:%M')
                planned_time_str = planned_time.strftime('%d.%m.%Y %H:%M')
                now = datetime.utcnow() + timedelta(hours=3)
                if planned_time < now:
                    result.is_valid = False
                    now_str = now.strftime('%d.%m.%Y %H:%M')
                    result.comment = f'Необходимо указать время из будущего! Время на сервере {now_str}, а вы указали {planned_time_str}.'
                else:
                    result.is_valid = True
                    result.planned_time = planned_time
                    result.planned_time_str = planned_time.strftime('%d.%m.%Y %H:%M')
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
                result.comment = f'Максимальная длина вопроса - {max_question_len} символов. В вашем вопросе {question_len} символов.'
            if question_len <= 0:
                result.is_valid = False
                result.comment = 'Вопрос должен содержать хотя бы один символ.'
        return result

    if any(word in text.lower() for word in ['закружился', 'закружилась', 'кружусь', 'кружимся', 'кружится']):
        result.type = MessageType.ZakruzhilasCommand
        return result

    result.type = MessageType.UnsupportedCommand
    return result
