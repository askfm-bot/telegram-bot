from typing import List
from repositories.bot_users_repository import BotUsersRepository
from models.bot_user import BotUser

class BotUsersProvider:
    def __init__(self, repository: BotUsersRepository):
        self.__repository = repository 

    def get(self) -> List[BotUser]:
        return self.__repository.get_all()
