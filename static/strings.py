from typing import List


class Strings:
    she = ['она', 'эта', 'Лапочка', 'Lapochka', 'порно гёрл','попьюлар гёрл', 'Мерлин Монро',
          'богема', 'царица', 'икона стиля', 'секс-символ', 'легендарная голивудская дива',
          'чудо чудное', 'умница-разумница', 'богиня', 'Мисс Вселенная', 'труженица', 'party girl',
          'королевишна', 'модница']

    found_time = ['снизошла', 'удосужилась', 'умудрилась', 'решила', 'соизволила', 'не постеснялась',
                 'нашла время, чтобы', 'посчитала нужным', 'отвлеклась от важной работы, чтобы',
                 'выкроила минутку в своём плотном расписании, чтобы', 'улучила минутку, чтобы',
                 'постаралась', 'не побрезговала', 'не погнушалась']

    @staticmethod
    def new(count: int) -> List[str]:
        def select(single: str, plural: str) -> str:
            if (count % 10 == 1) and (count % 100 != 11):
                return single
            return plural

        return [
            select('новый', 'новых'),
            select('важный', 'важных'),
            select('животрепещущий', 'животрепещущих')
        ]

    @staticmethod
    def question(count: int) -> str:
        if (count % 10 == 1) and (count % 100 != 11):
            return'вопрос'
        if (count % 10 in [2, 3, 4]) and (count % 100 not in [12, 13, 14]):
            return 'вопроса'
        return 'вопросов'

    @staticmethod
    def capitalize(value: str) -> str:
        if value:
            return value[0].capitalize() + value[1:]
        return value
