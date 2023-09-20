from config import users, sessions, questions_all, full_base
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

    is_random = True
    match mode:

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
    """Генерирует текст вопроса и количество ответов, а также номер верного ответа"""
    res = sessions.print_table('questions', 'amount', where=f'user_id = {user_id} and mode = "{mode}" and status = 0')

    if not res:
        return "Ошибка, сессия не найдена, начните новую сессию!"

    questions, amount = res[0]
    number_current_question = amount - len(questions.split())
    current_question = int(questions.split()[0])
    len_answers = len(full_base[questions_all[current_question]])
    text_msg = f"#{current_question}\nВопрос №{number_current_question}\n" \
               f"(Осталось вопросов: {len(questions.split())}):" \
               f"\n{questions_all[current_question].replace('@','')}\n\nВыберите один ответ:\n"
    correct_answer = None

    for index, answer in enumerate(full_base[questions_all[current_question]]):
        text_msg += f"{index+1}: {answer.replace('$','')}\n"
        if "$" in answer:
            correct_answer = index

    return text_msg, len_answers, correct_answer
