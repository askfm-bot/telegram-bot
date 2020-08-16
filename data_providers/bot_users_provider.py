from repositories import BotUsersRepository


def get():
    repository = BotUsersRepository()
    return repository.get_all()