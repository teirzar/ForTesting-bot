from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage


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
    with open('logs/log.txt', 'a', encoding='UTF-8') as log:
        text = f'{await get_time()}: {string}\n'
        log.write(text)


def start_stop(is_stop=False):
    text_message = f"Бот {'остановлен' if is_stop else 'запущен'}"

    async def func(bot: Bot):
        await add_log(f"!! {text_message} !!")
        print(text_message)
        await bot.send_message(210189427, text_message)

    return func


async def main() -> None:
    """Старт бота"""
    bot = Bot(token=get_token())
    dp = Dispatcher(storage=MemoryStorage())

    dp.startup.register(start_stop())
    dp.shutdown.register(start_stop(is_stop=True))
    from handlers import register_message_handlers, register_fsm_handlers, register_callback_handlers

    register_fsm_handlers(dp)
    register_message_handlers(dp)
    register_callback_handlers(dp)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
