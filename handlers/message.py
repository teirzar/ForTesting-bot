from aiogram.types import Message
from aiogram import Bot, Dispatcher, F
from keyboadrs import kb_main_menu, kb_profile_menu, kb_select_session, kb_inline_testing
from functions import is_new_session, create_new_session, get_question


async def cmd_main_menu(message: Message, bot: Bot):
    """Обработчик клавиатуры kb_main_menu"""
    await bot.send_message(message.from_user.id, f'Главное меню.', reply_markup=kb_main_menu())


async def cmd_mode_selection(message: Message):
    """Функция для запуска определенного режима"""
    mode, user_id = message.text, message.from_user.id
    if await is_new_session(mode, user_id):
        await create_new_session(mode, user_id)
    else:
        text_msg = "У вас уже есть активная сессия, хотите продолжить?"
        return await message.answer(text_msg, reply_markup=kb_select_session(mode))

    text_msg, len_answers, correct_answer = await get_question(mode, user_id)
    await message.answer(text_msg, reply_markup=kb_inline_testing(len_answers, correct_answer))


async def cmd_profile_menu(message: Message, bot: Bot):
    """Функция для вызова клавиатуры меню профиля и генерации текста статистики пользователя"""
    await bot.send_message(message.from_user.id, f'Профиль.', reply_markup=kb_profile_menu())


def register_message_handlers(dp: Dispatcher):
    """Регистратор обработчиков сообщений"""
    dp.message.register(cmd_main_menu, F.text == "/menu")
    dp.message.register(cmd_main_menu, F.text == "Главное меню")

    dp.message.register(cmd_mode_selection, F.text == "Режим изучения")
    dp.message.register(cmd_mode_selection, F.text == "Обычный режим")
    dp.message.register(cmd_mode_selection, F.text == "Режим экзамена")
    dp.message.register(cmd_mode_selection, F.text == "Режим марафона")
    dp.message.register(cmd_mode_selection, F.text == "Случайный режим")
    # dp.message.register(cmd_mode_selection, F.text == "Работа над ошибками")

    dp.message.register(cmd_profile_menu, F.text == "Мой профиль")


