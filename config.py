from aiogram import Bot, Dispatcher
from db import DBconnect
from aiogram.fsm.storage.memory import MemoryStorage
from functions import get_token


# переменные для запуска бота
TOKEN = get_token()
storage = MemoryStorage()
bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=storage)


# расположение файла с базой
src = "db/db_bot.db"
# подключение таблиц базы данных
users = DBconnect("users", src)
sessions = DBconnect("sessions", src)
