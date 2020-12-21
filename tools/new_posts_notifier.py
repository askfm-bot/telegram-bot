import time
import random
from telebot import TeleBot
from repositories.bot_users_repository import BotUsersRepository
from repositories.last_posts_repository import LastPostsRepository
from repositories.post_archive_repository import PostsArchiveRepository
from repositories.question_queue_repository import QuestionQueueRepository
from static.strings import Strings
from tools.site_parser import SiteParser
from tools.question_sender import QuestionSender


class NewPostsNotifier:
    def __init__(self,
                 bot: TeleBot,
                 site_parser: SiteParser,
                 question_sender: QuestionSender,
                 posts_archive_repository: PostsArchiveRepository,
                 last_posts_repository: LastPostsRepository,
                 bot_user_repository: BotUsersRepository,
                 questions_queue_repository: QuestionQueueRepository):
        self.__bot = bot
        self.__site_parser = site_parser
        self.__question_sender = question_sender
        self.__posts_archive_repository = posts_archive_repository
        self.__last_posts_repository = last_posts_repository
        self.__bot_user_repository = bot_user_repository
        self.__questions_queue_repository = questions_queue_repository
        
    @staticmethod
    def __get_title_message(question_count: int) -> str:
        part1 = Strings.capitalize(random.choice(Strings.she))
        part2 = random.choice(Strings.found_time)
        part3 = random.choice(['аж ', ''])
        part4 = random.choice(Strings.new(question_count)) + ' ' + Strings.question(question_count)
        return f'{part1} {part2} ответить {part3}на {question_count} {part4}:'

    def notify(self) -> None:
        questions = self.__site_parser.parse()
        last_date = self.__last_posts_repository.get_last_post_time()
        new_questions = [q for q in questions if q.time > last_date]

        if not new_questions:
            return

        self.__posts_archive_repository.add_many(new_questions)

        for question in new_questions:
            if question.title:
                self.__questions_queue_repository.mark_as_answered(question.title.strip())

        self.__last_posts_repository.update_last_post_time(new_questions[0].time)

        for user in self.__bot_user_repository.get_subscribed_to_notifications():
            title = NewPostsNotifier.__get_title_message(len(new_questions))
            unsubscribe = True

            try:
                self.__bot.send_message(user.id, title)
                unsubscribe = False
            except:
                pass

            try:
                self.__question_sender.send_many(user.id, new_questions)
                unsubscribe = False
            except:
                pass

            if unsubscribe:
                self.__bot_user_repository.update_is_subscribed(user.id, False)

            time.sleep(5)
