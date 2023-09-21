from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher, F
from functions import create_new_session, get_question, set_answer
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

    res = await get_question(mode, user_id)
    if type(res) == str:
        return await callback.answer(res, show_alert=True)

    text_msg, len_answers, correct_answer, current = res
    is_studying = mode == "101"
    kb = kb_inline_testing(mode, len_answers, correct_answer, current, is_studying=is_studying)
    await bot.send_message(user_id, text_msg, reply_markup=kb)
    await callback.answer(text=cb_text, show_alert=True)


async def cmd_inline_testing(callback: CallbackQuery, bot: Bot):
    """Основная функция работы тестирования"""
    user_id = callback.from_user.id
    mode, value, question, cmd = callback.data.split("_")[1:]
    res = await get_question(mode, user_id)
    is_studying = mode == "101"

    if type(res) == str:
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.answer(res, show_alert=True)
    text_msg, len_answers, correct_answer, current_question = res

    if str(question) != str(current_question):
        await callback.answer("Ошибка сессии. Ответ на вопрос был дан!", show_alert=True)
        return await callback.message.edit_reply_markup(reply_markup=None)

    if cmd == "open":
        kb = kb_inline_testing(mode, len_answers, correct_answer, question, is_studying=True) if value == 'hide' \
            else kb_inline_testing(mode, len_answers, correct_answer, question, is_studying=True, show=True)

        await callback.answer()
        return await callback.message.edit_reply_markup(reply_markup=kb)

    user_answer_res = await set_answer(user_id, mode, question, cmd)
    text_msg += f"\n\n{user_answer_res}" + (f"\nВерный ответ: {correct_answer + 1}." if is_studying else "")
    await callback.message.edit_text(text=text_msg, reply_markup=None)

    res = await get_question(mode, user_id)
    if type(res) == str:
        return await callback.answer(res, show_alert=True)

    text_msg, len_answers, correct_answer, current = res
    kb = kb_inline_testing(mode, len_answers, correct_answer, current, is_studying=is_studying)
    await bot.send_message(user_id, text_msg, reply_markup=kb)
    await callback.answer(text=user_answer_res)


def register_callback_handlers(dp: Dispatcher):
    """Регистратор обработчиков inline-сообщений"""
    dp.callback_query.register(cmd_select_session, F.data.startswith("session_"))
    dp.callback_query.register(cmd_inline_testing, F.data.startswith("test_"))
