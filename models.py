import emoji


class BotUser:
    def __init__(self, id, full_name, username, is_subscribed_to_notifications):
        self.id = id
        self.full_name = full_name
        self.username = username
        self.is_subscribed_to_notifications = is_subscribed_to_notifications


class Question:
    def __init__(self, title, time, time_relative, who_asked, answer, image_url):
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
        return emoji.emojize(f':question:ВОПРОС\n{self.title}\n\n:clock3: ВРЕМЯ\n{time_str}\n\n' + \
               f':bust_in_silhouette: КТО СПРОСИЛ\n{who_asked_str}\n\n:white_check_mark: ОТВЕТ{answer_str}', use_aliases=True)


class QuestionQueueItem:
    def __init__(self, text, time_created, time_planned, time_sended, status, added_by_id, added_by_name, has_answer):
        self.text = text
        self.time_created = time_created
        self.time_planned = time_planned
        self.time_sended = time_sended
        self.status = status # 0 - Unprocessed, 1 - Processed, 2 - InProgress, 3 - Error, 4 - ManualInserted
        self.added_by_id = added_by_id
        self.added_by_name = added_by_name
        self.has_answer = has_answer