from datetime import datetime


def get_token() -> str:
    """Функция читает файл key.txt в директории private.
    Внести в него свой токен!"""
    with open('private/key.txt', 'r') as file:
        token = file.readline()
        return token


async def get_time() -> str:
    """Возвращает строку времени в формате ГГГГ-ММ-ДД ЧЧ:ММ"""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


async def add_log(string) -> None:
    """Функция логирования.
    Вносит в txt файл данные в формате 'Время: событие' """
    with open('logs/log.txt', 'a') as log:
        text = f'{await get_time()}: {string}\n'
        log.write(text)
