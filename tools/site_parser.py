from typing import List, Optional
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from models.question import Question


class SiteParser:
    def __init__(self, url: str):
        self.__url = url

    def parse(self, count=-1) -> List[Question]:
        def get_title(article) -> str:
            return article.find('header').find('h2').contents[0]

        def get_time(article) -> datetime:
            time_tag = article.find('div', {'class': 'streamItem_properties'}).find('time')
            time = datetime.strptime(time_tag['datetime'], '%Y-%m-%dT%H:%M:%S')
            return time

        def get_time_relative(article) -> str:
            time_tag = article.find('div', {'class': 'streamItem_properties'}).find('time')
            time_relative = time_tag.contents[0]
            return time_relative

        def get_who_asked(article) -> Optional[str]:
            try:
                return article.find('span', {'class': 'author_username'}).contents[0]
            except:
                return None

        def get_answer(article) -> Optional[str]:
            try:
                contents = []
                for content in article.find('div', {'class': 'streamItem_content'}).contents:
                    content_str = str(content)
                    if content_str and not content_str.startswith('<'):
                        contents.append(content_str.strip())
                return '\n'.join(contents)
            except:
                pass

            try:
                return article.find('div', {'class': 'asnwerCard_text'}).contents[0]
            except:
                pass

            try:
                unlock_tag = article.find('div', {'class': 'lockedAnswer'}).find('a', {'class': 'btn-primary'})
                return f'{unlock_tag.contents[0]} (locked answer)'
            except:
                pass

            return None

        def get_image_url(article) -> Optional[str]:
            try:
                return article.find('div', {'class': 'streamItem_visual'}).find('a')['data-url']
            except:
                return None

        def build_question(article) -> Question:
            return Question(
                title=get_title(article),
                time=get_time(article),
                time_relative=get_time_relative(article),
                who_asked=get_who_asked(article),
                answer=get_answer(article),
                image_url=get_image_url(article)
            )

        html = requests.get(self.__url)
        root = BeautifulSoup(html.content, 'html.parser')
        articles = root.find_all('article')
        if count >= 0:
            articles = articles[0:count]

        return [build_question(article) for article in articles]
