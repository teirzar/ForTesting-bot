from config import users, sessions, questions_all, full_base, names
from random import randint


async def get_users() -> list:
    """Возвращает ID всех пользователей"""
    res = users.print_table('id')
    if res:
        return [user[0] for user in res]
    return []


async def register(user_id, name, personnel_number) -> None:
    """Функция для регистрации пользователя в базе данных"""
    users.write('id', 'name', 'personnel_number', values=f'{user_id}, "{name}", {personnel_number}')


async def is_new_session(mode, user_id) -> bool:
    """Проверяет, есть ли у пользователя запущенные тесты"""
    return not bool(sessions.print_table('questions', where=f'mode = "{mode}" and user_id = {user_id} and status = 0'))


def questions_generate(length, is_random=True) -> list:
    """Функция генерации порядка вопросов"""
    if not is_random:
        return [str(i) for i in range(length)]

    lst = []
    while len(lst) != length:
        num = randint(0, 204)
        if str(num) in lst:
            continue
        lst.append(str(num))
    return lst


async def create_new_session(mode, user_id) -> None:
    """Создает новую сессию для пользователя, загружает номера вопросов в базу данных"""
    if not await is_new_session(mode, user_id):
        sessions.update('status = 1', where=f'user_id = {user_id} and mode = "{mode}"')

    name_mode = await get_name_mode(mode)

    is_random = True
    match name_mode:

        case "Режим изучения" | "Режим марафона":
            is_random, length = False, 204

        case "Обычный режим":
            length = 20

        case "Режим экзамена":
            length = 10

        case "Случайный режим":
            length = 204

        case "Работа над ошибками":
            length = 1

    questions = " ".join(questions_generate(length, is_random=is_random)).strip()

    sessions.write('user_id', 'mode', 'questions', 'amount', 'status',
                   values=f'{user_id}, "{mode}", "{questions}", {length}, 0')


async def get_question(mode, user_id) -> tuple | str:
    """Генерирует текст вопроса и количество ответов, а также номер верного ответа и номер текущего вопроса"""
    res = sessions.print_table('questions', 'amount', where=f'user_id = {user_id} and mode = "{mode}" and status = 0')

    if not res:
        return "Ошибка, сессия не найдена, начните новую сессию!"

    questions, amount = res[0]
    if not questions:
        return "Вопросы закончились, начните новую сессию!"

    number_current_question = amount - len(questions.split())
    current_question = int(questions.split()[0])
    len_answers = len(full_base[questions_all[current_question]])
    text_msg = f"#{current_question}\nВопрос №{number_current_question + 1}\n" \
               f"(Осталось вопросов: {len(questions.split()) - 1}):" \
               f"\n{questions_all[current_question].replace('@','')}\n\nВыберите один ответ:\n"
    correct_answer = None

    for index, answer in enumerate(full_base[questions_all[current_question]]):
        text_msg += f"{index+1}: {answer.replace('$','')}\n"
        if "$" in answer:
            correct_answer = index

    return text_msg, len_answers, correct_answer, current_question


async def get_number_mode(mode) -> int:
    """Функция возвращает кодовое обозначение режима по названию режима"""
    return names.print_table("number", where=f'name = "{mode}"')[0][0]


async def get_name_mode(number) -> str:
    """Функция возвращает название режима по его кодовому обозначению"""
    return names.print_table("name", where=f'number = {number}')[0][0]


async def set_answer(user_id, mode, question, cmd):
    """Функция помещает ошибочный ответ в ошибки, а верный ответ удаляет из списка вопросов"""
    current_questions = sessions.print_table('questions', where=f'user_id = {user_id} and mode = {mode} and status = 0')

    current_questions = current_questions[0][0].split()
    new_questions = " ".join([el for el in current_questions[1:]])

    if cmd == "mistake":
        current_mistakes = users.print_table('mistakes', where=f'id = {user_id}')[0][0]
        if current_mistakes:
            if question not in current_mistakes.split():
                users.update(f'mistakes = "{current_mistakes} {question}"', where=f'id = {user_id}')
        else:
            users.update(f'mistakes = "{question}"', where=f'id = {user_id}')
        sessions.update(f'mistakes = mistakes + 1, questions = "{new_questions}"',
                        where=f'user_id = {user_id} and mode = {mode} and status = 0')
        return "Ответ неверный!"

    sessions.update(f'questions = "{new_questions}"', where=f'user_id = {user_id} and mode = {mode} and status = 0')
    return "Верно!"
