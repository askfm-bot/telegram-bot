import requests
from datetime import datetime
from bs4 import BeautifulSoup
from config import URL_FEED
from models import Question

class SiteParser:
    @staticmethod
    def parse(count=-1):
        def get_title(article):
            return article.find('header').find('h2').contents[0]

        def get_time(article):
            time_tag = article.find('div', { 'class': 'streamItem_properties' }).find('time')
            time = datetime.strptime(time_tag['datetime'], '%Y-%m-%dT%H:%M:%S')
            return time

        def get_time_relative(article):
            time_tag = article.find('div', { 'class': 'streamItem_properties' }).find('time')
            time_relative = time_tag.contents[0]
            return time_relative

        def get_who_asked(article):
            try:
                return article.find('span', { 'class': 'author_username' }).contents[0]
            except:
                return None

        def get_answer(article):
            try:
                return '\n'.join([str(e).strip() for e in article.find('div', { 'class': 'streamItem_content' }).contents if str(e) and not str(e).startswith('<')])
            except:
                pass

            try:
                return article.find('div', { 'class': 'asnwerCard_text' }).contents[0]
            except:
                pass

            try:
                unlock_tag = article.find('div', { 'class': 'lockedAnswer' }).find('a', { 'class': 'btn-primary' })
                return f'{unlock_tag.contents[0]} (locked answer)'
            except:
                return None

        def get_image_url(article):
            try:
                return article.find('div', { 'class': 'streamItem_visual' }).find('a')['data-url']
            except:
                return None

        html = requests.get(URL_FEED)
        root = BeautifulSoup(html.content, 'html.parser')
        articles = root.find_all('article')
        if (count >= 0):
            articles = articles[0:count]

        return [
            Question(
                title=get_title(article),
                time=get_time(article),
                time_relative=get_time_relative(article),
                who_asked=get_who_asked(article),
                answer=get_answer(article),
                image_url=get_image_url(article)
            )
            for article in articles
        ]