import requests
from datetime import datetime
from bs4 import BeautifulSoup
import emoji
from config import URL


class Question:
    def __init__(self, title, time, time_str, who_asked, answer):
        self.title = title
        self.time = time
        self.time_str = time_str
        self.who_asked = who_asked
        self.answer = answer

    def __repr__(self):
        who_asked_str = self.who_asked if self.who_asked else 'в душе не ебу'
        return emoji.emojize(f':question:ВОПРОС\n{self.title}\n\n:clock3: ВРЕМЯ\n{self.time_str}\n\n' + \
               f':bust_in_silhouette: КТО СПРОСИЛ\n{who_asked_str}\n\n:white_check_mark: ОТВЕТ\n{self.answer}', use_aliases=True)


def get_questions(count=-1):
    html = requests.get(URL)
    root = BeautifulSoup(html.content, 'html.parser')
    articles = root.find_all('article')
    if (count >= 0):
        articles = articles[0:count]
    questions = []
    
    for article in articles:
        title = article.find('header').find('h2').contents[0]
        time_tag = article.find('div', { 'class': 'streamItem_properties' }).find('time')
        time = datetime.strptime(time_tag['datetime'], '%Y-%m-%dT%H:%M:%S')
        time_str = time_tag.contents[0]
        who_asked = article.find('span', { 'class': 'author_username' })
        who_asked = who_asked.contents[0] if who_asked else None
        answer = '\n'.join([str(e).strip() for e in article.find('div', { 'class': 'streamItem_content' }).contents if str(e) and not str(e).startswith('<')])
        questions.append(Question(title, time, time_str, who_asked, answer))

    return questions