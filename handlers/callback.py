from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher, F
from functions import create_new_session, get_question
from keyboadrs import kb_inline_testing
import asyncio


async def cmd_select_session(callback: CallbackQuery, bot: Bot):
    """Функция для работы с сессиями (создать новую сессию/продолжить старую)"""
    user_id = callback.from_user.id
    cmd, mode = callback.data.split("_")[1:]

    match cmd:
        case "continue":
            cb_text = "Продолжаем решение."

        case "new":
            await create_new_session(mode, user_id)
            cb_text = "Новая сессия создана!"

    await callback.message.delete()

    text_msg, len_answers, correct_answer, current = await get_question(mode, user_id)
    await bot.send_message(user_id, text_msg, reply_markup=kb_inline_testing(mode, len_answers, correct_answer, current))
    await callback.answer(text=cb_text, show_alert=True)


async def cmd_inline_testing(callback: CallbackQuery, bot: Bot):
    """Основная функция работы тестирования"""


def register_callback_handlers(dp: Dispatcher):
    """Регистратор обработчиков inline-сообщений"""
    dp.callback_query.register(cmd_select_session, F.data.startswith("session_"))
    dp.callback_query.register(cmd_inline_testing, F.data.startswith("test_"))
