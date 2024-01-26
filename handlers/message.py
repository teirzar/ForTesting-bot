from aiogram.types import Message
from aiogram.types.input_file import FSInputFile
from aiogram import Bot, Dispatcher, F
from keyboadrs import kb_main_menu, kb_profile_menu, kb_select_session, kb_inline_testing
from functions import is_new_session, create_new_session, get_question, get_number_mode, get_user_mistakes
from functions import get_full_text_info, add_log, change_mode
from utils import HELP_MESSAGE


async def cmd_main_menu(message: Message, bot: Bot):
    """Обработчик клавиатуры kb_main_menu"""
    await add_log(f"[{message.from_user.id}] открыл Главное меню")
    await bot.send_message(message.from_user.id, f'Главное меню.', reply_markup=kb_main_menu())


async def cmd_mode_selection(message: Message):
    """Функция для запуска определенного режима"""
    name_mode, user_id = message.text, message.from_user.id
    mode = await get_number_mode(name_mode)
    is_studying = name_mode == "Режим изучения"

    if await is_new_session(mode, user_id):
        await add_log(f"[{user_id}] создана новая сессия mode [{mode}]")
        await create_new_session(mode, user_id)
    else:
        text_msg = "У вас уже есть активная сессия, хотите продолжить?"
        await add_log(f"[{user_id}] открыл меню сессии mode [{mode}]")
        return await message.answer(text_msg, reply_markup=kb_select_session(mode))

    text_msg, len_answers, correct_answer, question, _ = await get_question(mode, user_id)

    kb = kb_inline_testing(mode, len_answers, correct_answer, question, is_studying=is_studying)
    await message.answer(text_msg, reply_markup=kb)


async def cmd_profile_menu(message: Message, bot: Bot):
    """Функция для вызова клавиатуры меню профиля и генерации текста статистики пользователя"""
    user_id = message.from_user.id
    text_msg = await get_full_text_info(user_id)
    await add_log(f"[{user_id}] открыл профиль.")
    await bot.send_message(user_id, f'Ваш профиль.\n{text_msg}', reply_markup=kb_profile_menu(), parse_mode='html')


async def cmd_mode_mistakes(message: Message, bot: Bot):
    """Функция для обработки нажатия на кнопку "работа над ошибками" """
    user_id = message.from_user.id
    mistakes = await get_user_mistakes(user_id)
    if not mistakes:
        return await bot.send_message(user_id, "Список ваших ошибок пуст.")

    await bot.send_message(user_id, f"У вас {len(mistakes.split())} ошибок.")
    await add_log(f"[{user_id}] открыл Работу над ошибками")
    text_msg, len_answers, correct_answer, question, _ = await get_question(106, user_id, is_mistakes=True)
    kb = kb_inline_testing(106, len_answers, correct_answer, question, is_studying=True)
    return await message.answer(text_msg, reply_markup=kb)


async def cmd_help_button(message: Message, bot: Bot):
    """Функция для работы кнопки "Помощь". """
    user_id = message.from_user.id
    await add_log(f"[{user_id}] открыл Помощь")
    return await bot.send_message(user_id, HELP_MESSAGE, parse_mode='html')


async def cmd_get(message: Message, bot: Bot):
    """Функция обработки get запросов и отправки соответствующего файла"""
    user_id = message.from_user.id
    cmd = message.text[5:]
    await add_log(f"[{user_id}] запросил [{cmd}]")
    if user_id != 210189427:
        await add_log(f"[{user_id}] отказ в доступе [{cmd}]")
        return await message.answer("Отказ в доступе.")
    if cmd == "db":
        doc = 'db/db_bot.db'
    elif cmd == "log":
        doc = 'logs/log.txt'
    else:
        await add_log(f"[{user_id}] неудачное отправление [{cmd}]")
        return
    await add_log(f"[{user_id}] успешно отправлено [{cmd}]")
    await bot.send_document(user_id, FSInputFile(doc))
    return


async def cmd_change_mode(message: Message, bot: Bot):
    """Функция для включения и отключения перемешивания вариантов ответа в вопросе"""
    user_id = message.from_user.id
    out_message = await change_mode(user_id)
    return await bot.send_message(user_id, out_message)


def register_message_handlers(dp: Dispatcher):
    """Регистратор обработчиков сообщений"""
    dp.message.register(cmd_main_menu, F.text == "/menu")
    dp.message.register(cmd_main_menu, F.text == "Главное меню")

    dp.message.register(cmd_mode_selection, F.text == "Режим изучения")
    dp.message.register(cmd_mode_selection, F.text == "Обычный режим")
    dp.message.register(cmd_mode_selection, F.text == "Режим экзамена")
    dp.message.register(cmd_mode_selection, F.text == "Режим марафона")
    dp.message.register(cmd_mode_selection, F.text == "Случайный режим")

    dp.message.register(cmd_mode_mistakes, F.text == "Работа над ошибками")

    dp.message.register(cmd_main_menu, F.text == "/profile")
    dp.message.register(cmd_profile_menu, F.text == "Мой профиль")
    dp.message.register(cmd_change_mode, F.text == "Перемешивание вариантов ответа")

    dp.message.register(cmd_help_button, F.text == "/help")

    dp.message.register(cmd_get, F.text.startswith("/get_"))
