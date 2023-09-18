from db import DBconnect

# расположение файла с базой
src = "db/db_bot.db"
# подключение таблиц базы данных
users = DBconnect("users", src)
sessions = DBconnect("sessions", src)
