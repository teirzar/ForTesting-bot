from db import DBconnect

# расположение файла с базой
src = "db/db_bot.db"
# подключение таблиц базы данных
users = DBconnect("users", src)
sessions = DBconnect("sessions", src)
names = DBconnect("names", src)


def base_init():
    """Загружаем базу с вопросами и ответами, а также просто вопросы"""
    f = open('static/questions.txt', 'r', encoding="utf-8")
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
