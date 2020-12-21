from typing import List
import requests
from io import BytesIO
from telebot import TeleBot
from models.question import Question


class QuestionSender:
    def __init__(self, bot: TeleBot):
        self.__bot = bot

    def send(self, chat_id: int, question: Question) -> None:
        self.__bot.send_message(chat_id, question)
        if question.image_url:
            try:
                response = requests.get(question.image_url)
                self.__bot.send_photo(chat_id, BytesIO(response.content))
            except:
                pass

    def send_many(self, chat_id: int, questions: List[Question]) -> None:
        for question in questions:
            self.send(chat_id, question)
