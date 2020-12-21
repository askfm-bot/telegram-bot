import time
from tools.question_queue_handler import QuestionQueueHandler
from tools.vk_user_status_provider import VkUserOnlineStatusProvider
from tools.vk_online_status_collector import VkUserOnlineStatusCollector
from repositories.question_queue_repository import QuestionQueueRepository
from repositories.vk_user_online_statuses_repository import VkUserOnlineStatusesRepository
from config import VK_ACCESS_TOKEN, VK_USER_ID


def run_question_queue_handler():
    try:
        handler = QuestionQueueHandler(
            QuestionQueueRepository()
        )
        handler.process()
    except:
        print('QuestionQueueHandler error')


def run_vk_user_online_status_collector():
    try:
        collector = VkUserOnlineStatusCollector(
            VkUserOnlineStatusProvider(VK_USER_ID, VK_ACCESS_TOKEN),
            VkUserOnlineStatusesRepository()
        )
        collector.collect()
    except:
        print('VkUserOnlineStatusCollector error')


if __name__ == '__main__':
    run_question_queue_handler()
    time.sleep(10)
    run_vk_user_online_status_collector()
