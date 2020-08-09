import requests
from datetime import datetime
from bs4 import BeautifulSoup
from config import URL
from models import Question


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
        time_relative = time_tag.contents[0]
        who_asked = article.find('span', { 'class': 'author_username' })
        who_asked = who_asked.contents[0] if who_asked else None
        answer = '\n'.join([str(e).strip() for e in article.find('div', { 'class': 'streamItem_content' }).contents if str(e) and not str(e).startswith('<')])
        questions.append(Question(title, time, time_relative, who_asked, answer))

    return questions