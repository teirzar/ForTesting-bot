from utils.db import DBconnect

# расположение файла с базой
src = "./db/db_bot.db"
# подключение таблиц базы данных
users = DBconnect("users", src)
sessions = DBconnect("sessions", src)
names = DBconnect("names", src)


def base_init():
    """Загружаем базу с вопросами и ответами, а также просто вопросы"""
    f = open('./static/questions.txt', 'r', encoding="utf-8")
    arr = []
    answers = dict()
    temp = ''
    temp_set = set()
    for line in f:
        if "@" in line:
            if len(temp_set) != 0:
                answers[temp] = list(temp_set)
                temp_set.clear()
            arr.append(line)
            temp = line
            answers[line] = ""
        else:
            temp_set.add(line.replace("\n", ""))
    f.close()
    return arr[0:len(arr) - 1], answers


questions_all, full_base = base_init()  # инициализируем базу вопросов и ответов


HELP_MESSAGE = """Данный бот предоставляет возможность решать тесты по электробезопасности в телеграмме. 
Главное меню открывается командой <code>Главное меню</code> (/menu)
Для того, чтобы посмотреть свою статистику или изменить личные данные, зайдите в <code>Мой профиль</code> (/profile).
Вы можете выбрать один из шести режимов решения:
<code>Режим изучения</code> - вопросы идут по очереди и включены подсказки
<code>Обычный режим</code> - 20 случайных вопросов, подсказки отключены
<code>Режим экзамена</code> - 10 случайных вопросов, право на 3 ошибки, подсказки отключены
<code>Режим марафона</code> - Все вопросы подряд, задаются по порядку
<code>Случайный режим</code> - Все вопросы подряд, задаются вперемешку
<code>Работа над ошибками</code> - Решение собственных ошибок, допущенных во время решения в других режимах

Бот разработан Ульянчиком Н.А. для себя, и для СТТП парка на добровольных началах :) 
Предложения по улучшению задавать лично. @jinmnij
"""
