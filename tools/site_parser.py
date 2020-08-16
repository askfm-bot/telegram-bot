import requests
from datetime import datetime
from bs4 import BeautifulSoup
from config import URL_FEED
from models import Question


def get_questions(count=-1):
    html = requests.get(URL_FEED)
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

        try:
            who_asked = article.find('span', { 'class': 'author_username' }).contents[0]
        except:
            who_asked = None

        try:
            answer = '\n'.join([str(e).strip() for e in article.find('div', { 'class': 'streamItem_content' }).contents if str(e) and not str(e).startswith('<')])
        except:
            try:
                answer = article.find('div', { 'class': 'asnwerCard_text' }).contents[0]
            except:
                answer = None

        try:
            image_url = article.find('div', { 'class': 'streamItem_visual' }).find('a')['data-url']
        except:
            image_url = None

        questions.append(Question(title, time, time_relative, who_asked, answer, image_url))

    return questions