from utils import users, sessions, questions_all, full_base, names
from random import randint, shuffle
from functions import add_log


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
        num = randint(0, 203)
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
            is_random, length = False, 203

        case "Обычный режим":
            length = 20

        case "Режим экзамена":
            length = 10

        case "Случайный режим":
            length = 203

        case "Работа над ошибками":
            length = 1

    questions = " ".join(questions_generate(length, is_random=is_random)).strip()

    sessions.write('user_id', 'mode', 'questions', 'amount', 'status',
                   values=f'{user_id}, "{mode}", "{questions}", {length}, 0')


async def get_question(mode, user_id, is_mistakes=False, is_hide_show=None) -> tuple | str | int:
    """Генерирует текст вопроса и количество ответов, а также номер верного ответа и номер текущего вопроса"""
    if is_mistakes:
        mistakes = await get_user_mistakes(user_id)
        mistakes_count = len(mistakes.split())
        res = (mistakes, mistakes_count)
    else:
        res = sessions.print_table('questions', 'amount',
                                   where=f'user_id = {user_id} and mode = "{mode}" and status = 0')

    if not res:
        await add_log(f"[{user_id}] ошибка сессии mode [{mode}]")
        return "Ошибка, сессия не найдена, начните новую сессию!"

    questions, amount = res if is_mistakes else res[0]

    if not questions:
        await add_log(f"[{user_id}] ошибка вопросов mode [{mode}]")
        return "Все задания решены!" if is_mistakes else "Вопросы закончились, начните новую сессию!"

    number_current_question = amount - len(questions.split())
    current_question = int(questions.split()[0])
    len_answers = len(full_base[questions_all[current_question]])
    text_msg = f"#{current_question}\nВопрос №{number_current_question + 1}\n" \
               f"(Осталось вопросов: {len(questions.split()) - 1}):" \
               f"\n{questions_all[current_question].replace('@','')}\n\nВыберите один ответ:\n"
    correct_answer = None
    correct_answer_text = ""

    if is_hide_show:
        return len_answers, int(is_hide_show.strip('hide').strip('show')), current_question

    if await get_shuffle_status(user_id):
        shuffle_indexes = list(range(len_answers))
        shuffle(shuffle_indexes)
        for i, i_shuffle in enumerate(shuffle_indexes):
            current_answer = full_base[questions_all[current_question]][i_shuffle]
            text_msg += f"{i+1}: {current_answer.replace('$', '')}\n"
            if "$" in current_answer:
                correct_answer = i
                correct_answer_text = current_answer.replace('$', '')
    else:
        for index, answer in enumerate(full_base[questions_all[current_question]]):
            text_msg += f"{index + 1}: {answer.replace('$', '')}\n"
            if "$" in answer:
                correct_answer = index
                correct_answer_text = answer.replace('$', '')

    return text_msg, len_answers, correct_answer, current_question, correct_answer_text


async def get_number_mode(mode) -> int:
    """Функция возвращает кодовое обозначение режима по названию режима"""
    return names.print_table("number", where=f'name = "{mode}"')[0][0]


async def get_name_mode(number) -> str:
    """Функция возвращает название режима по его кодовому обозначению"""
    return names.print_table("name", where=f'number = {number}')[0][0]


async def set_answer(user_id, mode, question, cmd, is_mistakes=False) -> str:
    """Функция помещает ошибочный ответ в ошибки, а верный ответ удаляет из списка вопросов"""
    current_questions = await get_user_mistakes(user_id) if is_mistakes else \
        sessions.print_table('questions', where=f'user_id = {user_id} and mode = {mode} and status = 0')

    current_questions = current_questions.split() if is_mistakes else current_questions[0][0].split()
    new_questions = " ".join([el for el in current_questions[1:]])
    change_status = "" if new_questions else ", status = 1"

    if cmd == "mistake":
        current_mistakes = await get_user_mistakes(user_id)

        if current_mistakes:
            if question not in current_mistakes.split():
                users.update(f'mistakes = "{current_mistakes} {question}"', where=f'id = {user_id}')
        else:
            users.update(f'mistakes = "{question}"', where=f'id = {user_id}')

        if is_mistakes:
            current_questions = await get_user_mistakes(user_id)
            new_questions = " ".join(current_questions.split()[1:])
            new_mistakes = f"{new_questions} {question}" if new_questions else question
            users.update(f'mistakes = "{new_mistakes}"', where=f'id = {user_id}')
            change_status = False

        else:
            sessions.update(f'mistakes = mistakes + 1, questions = "{new_questions}"{change_status}',
                            where=f'user_id = {user_id} and mode = {mode} and status = 0')

        return_text = "❌ Ответ неверный!"
        log_text = "неверный"

    else:
        if is_mistakes:
            users.update(f'mistakes = "{new_questions}"', where=f'id = {user_id}')
        else:
            sessions.update(f'questions = "{new_questions}"{change_status}',
                            where=f'user_id = {user_id} and mode = {mode} and status = 0')
        return_text = "✅ Верно!"
        log_text = "верный"

    await add_log(f'[{user_id}] ответ [{log_text}] на вопрос [{question}]')
    return return_text + (" Вопросы закончились." if change_status else "")


async def get_stats(user_id) -> str:
    """Функция генерации текста статистики за последнюю завершенную сессию"""
    last = sessions.print_table('amount', 'mistakes', 'questions', 'mode',
                                where=f'user_id = {user_id} and status = 1',
                                order_by='id DESC LIMIT 1',
                                )
    if not last:
        return "Статистика недоступна, вы не закончили ни одну сессию."

    amount, mistakes, questions, mode = last[0]
    mode = await get_name_mode(mode)
    questions = len(questions.split()) if questions else 0

    if not amount - questions:
        return f"Не было решено ни одного вопроса из {questions} вопросов. Ошибок допущено: {mistakes}"

    return f"За последнюю сессию в режиме [{mode}] вы дали ответы на {amount - questions} вопроса(-ов) и ошиблись " \
           f"{mistakes} раз(-а).\nИз {amount} вопроса(-ов) вам оставалось ответить на {questions} вопрос(-ов).\n" \
           f"Процент верных ответов: {round(100 - (mistakes/(amount - questions)) * 100, 2)}%.\n"


async def get_user_mistakes(user_id) -> None | str:
    """Функция возвращает текущие ошибки пользователя"""
    return users.print_table('mistakes', where=f'id = {user_id}')[0][0]


async def get_full_text_info(user_id) -> str:
    """Генерирует текст полной статистики в профиль пользователя"""
    name, pn = users.print_table('name', 'personnel_number', where=f'id = {user_id}')[0]
    text = f"<b>Ваше имя: {name}</b>\n<b>Ваш табельный номер: {pn}</b>\n\n"
    text += "<b>Общая статистика:</b>\n"
    res = sessions.print_table('questions', 'amount', 'mistakes', 'status', where=f'user_id = {user_id}')
    current_mistakes = await get_user_mistakes(user_id)
    current_mistakes = len(current_mistakes.split()) if current_mistakes else 0
    if not res:
        return f"{text} Статистика отсутствует."
    all_mistakes = 0
    all_amount = 0
    all_questions = 0
    current_questions = 0
    for q, a, m, s in res:
        all_questions += len(q.split()) if q else 0
        all_amount += a
        current_questions += len(q.split()) if q and s == 0 else 0
        all_mistakes += m

    text += f"Всего решено заданий: {all_amount - all_questions}\n" \
            f"Ошибок было допущено: {all_mistakes}\n" \
            f"Не решено в активных сессиях: {current_questions}\n" \
            f"В режиме работы над ошибками у Вас <b>{current_mistakes}</b> не исправленных заданий.\n"
    if all_amount - all_questions:
        text += f"Ваш процент верных ответов: {round(100 - (all_mistakes/(all_amount - all_questions)) * 100, 2)}%.\n"

    text += f"<b>Статистика за последнюю сессию:</b>\n{await get_stats(user_id)}"
    text += f"\n\nРежим перемешивания вариантов ответа [{'в' if await get_shuffle_status(user_id) else 'от'}ключён]"
    return text


async def end_session(user_id, mode) -> str | None:
    """Функция для завершения начатой сессии пользователем"""
    current_session = sessions.print_table(where=f'user_id = {user_id} and mode = {mode} and status = 0')
    if current_session:
        sessions.update('status = 1', where=f'user_id = {user_id} and mode = {mode} and status = 0')
        return
    return "Ошибка! У вас нет активной сессии. Завершать нечего."


async def failed_the_exam(user_id) -> bool | str:
    """Функция проверяет сколько ошибок допущено пользователем и допущен ли следующий вопрос"""
    res = sessions.print_table('mistakes', where=f'user_id = {user_id} and mode = 103 and status = 0')[0]
    if res:
        return res[0] >= 3
    return "Активная сессия не найдена."


async def get_shuffle_status(user_id) -> bool:
    """Возвращает состояние статуса перемешивания ответов в профиле"""
    return bool(users.print_table('shuffle', where=f'id = {user_id}')[0][0])


async def change_mode(user_id) -> str:
    """Функция для изменения состояния включения перемешивания вариантов ответа"""
    current = await get_shuffle_status(user_id)
    users.update(f'shuffle = {not current}', where=f'id = {user_id}')
    return f"Режим перемешивания вариантов ответа был {'от' if current else 'в'}ключён"
