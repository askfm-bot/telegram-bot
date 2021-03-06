from typing import Optional
from datetime import datetime
from emoji import emojize


class Question:
    def __init__(self, title: str, time: datetime, time_relative: Optional[str],
                 who_asked: str, answer: str, image_url: str):
        self.title = title
        self.time = time
        self.time_relative = time_relative
        self.who_asked = who_asked
        self.answer = answer
        self.image_url = image_url

    def __repr__(self):
        who_asked_str = self.who_asked if self.who_asked else 'в душе не ебу'
        time_str = self.time_relative if self.time_relative else self.time
        answer_str = f'\n{self.answer}' if self.answer else ''
        return emojize(f':question:ВОПРОС\n{self.title}\n\n:clock3: ВРЕМЯ\n{time_str}\n\n'
                       f':bust_in_silhouette: КТО СПРОСИЛ\n{who_asked_str}\n\n:white_check_mark: ОТВЕТ{answer_str}',
                       use_aliases=True)
