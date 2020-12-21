from bot import bot
from tools.site_parser import SiteParser
from tools.question_sender import QuestionSender
from tools.new_posts_notifier import NewPostsNotifier
from repositories.bot_users_repository import BotUsersRepository
from repositories.last_posts_repository import LastPostsRepository
from repositories.post_archive_repository import PostsArchiveRepository
from repositories.question_queue_repository import QuestionQueueRepository
from config import URL_FEED


if __name__ == '__main__':
    notifier = NewPostsNotifier(
        bot,
        SiteParser(URL_FEED),
        QuestionSender(bot),
        PostsArchiveRepository(),
        LastPostsRepository(),
        BotUsersRepository(),
        QuestionQueueRepository()
    )

    try:
        notifier.notify()
    except:
        print('New posts notification job error')
