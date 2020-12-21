from datetime import datetime
from telebot import TeleBot
from tools.vk_status_plot_builder import VkStatusPlotBuilder


class VkStatusPlotSender:
    def __init__(self, bot: TeleBot, plot_builder: VkStatusPlotBuilder):
        self.__bot = bot
        self.__plot_builder = plot_builder

    def send(self, time_utc_from: datetime, time_utc_to: datetime, chat_id: int) -> None:
        buffer = self.__plot_builder.build(time_utc_from, time_utc_to)
        self.__bot.send_photo(chat_id, buffer)
        buffer.close()
