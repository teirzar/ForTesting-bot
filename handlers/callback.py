from aiogram.types import CallbackQuery
from aiogram import Bot, Dispatcher, F
from functions import create_new_session, get_question, set_answer, get_stats, end_session, failed_the_exam, add_log
from keyboadrs import kb_inline_testing, kb_select_session
from aiogram.exceptions import TelegramRetryAfter


async def cmd_select_session(callback: CallbackQuery, bot: Bot):
    """Функция для работы с сессиями (создать новую сессию/продолжить старую)"""
    user_id = callback.from_user.id
    cmd, mode = callback.data.split("_")[1:]

    match cmd:
        case "continue":
            log_text = f"продолжает решение mode [{mode}]"
            cb_text = "Продолжаем решение."

        case "new":
            await create_new_session(mode, user_id)
            log_text = f"создал новую сессию mode [{mode}]"
            cb_text = "Новая сессия создана!"

    await callback.message.delete()

    res = await get_question(mode, user_id)
    if type(res) == str:
        return await callback.answer(res, show_alert=True)

    text_msg, len_answers, correct_answer, current, _ = res
    is_studying = mode == "101"
    kb = kb_inline_testing(mode, len_answers, correct_answer, current, is_studying=is_studying)
    await add_log(f"[{user_id}] {log_text}")
    try:
        await bot.send_message(user_id, text_msg, reply_markup=kb)
    except TelegramRetryAfter:
        await callback.answer(text="Сработал АНТИФЛУД! Подождите 5 минут и продолжайте решение.", show_alert=True)
    else:
        await callback.answer(text=cb_text, show_alert=True)


async def cmd_inline_testing(callback: CallbackQuery, bot: Bot):
    """Основная функция работы тестирования"""
    user_id = callback.from_user.id
    mode, value, question, cmd = callback.data.split("_")[1:]

    if cmd == "end":
        res = await end_session(user_id, mode)
        text_msg = await get_stats(user_id)
        await callback.message.edit_reply_markup(reply_markup=None)
        if not res:
            await bot.send_message(user_id, text_msg, reply_markup=kb_select_session(mode, is_select=False))

        await add_log(f"[{user_id}] добровольно завершил сессию досрочно mode [{mode}]")
        return await callback.answer(text_msg if res else "Сессия успешно завершена!", show_alert=True)

    is_mistakes = mode == "106"
    is_hide_show = value if (value.startswith("hide") or value.startswith("show")) else False
    res = await get_question(mode, user_id, is_mistakes=is_mistakes, is_hide_show=is_hide_show)
    is_exam = mode == "103"
    is_studying = mode == "101" or is_mistakes

    if type(res) == str:
        await callback.message.edit_reply_markup(reply_markup=None)
        return await callback.answer(res, show_alert=True)

    if is_hide_show:
        len_answers, correct_answer, current_question = res
    else:
        text_msg, len_answers, correct_answer, current_question, correct_answer_text = res

    if str(question) != str(current_question):
        await callback.answer("Ошибка сессии. Ответ на вопрос был дан или сессия была закончена!", show_alert=True)
        await add_log(f"[{user_id}] ошибка сессии mode [{mode}]")
        return await callback.message.edit_reply_markup(reply_markup=None)

    if cmd == "open":
        kb = kb_inline_testing(mode, len_answers, correct_answer, question, is_studying=True) \
            if value.startswith('hide') \
            else kb_inline_testing(mode, len_answers, correct_answer, question, is_studying=True, show=True)
        await add_log(f"[{user_id}] {'за' if value.startswith('hide') else 'от'}крыл подсказку вопроса [{question}]")
        await callback.answer()
        return await callback.message.edit_reply_markup(reply_markup=kb)

    user_answer_res = await set_answer(user_id, mode, question, cmd, is_mistakes=is_mistakes)
    text_msg += f"\n\n{user_answer_res}" + (f"\nВерный ответ: {correct_answer_text}." if is_studying else "")
    try:
        await callback.message.edit_text(text=text_msg, reply_markup=None)
    except TelegramRetryAfter:
        await callback.answer(text="Сработал АНТИФЛУД! Подождите 5 минут и продолжайте решение.", show_alert=True)


    res = await get_question(mode, user_id, is_mistakes=is_mistakes)

    if user_answer_res.endswith("."):
        res = "Вопросы закончились!" + ("" if is_mistakes else "Взгляните на статистику.")
        res += "\n\nЭкзамен сдан" if is_exam else ''
        if not is_mistakes:
            await bot.send_message(user_id, text=await get_stats(user_id) + ("\n\nЭкзамен сдан!" if is_exam else ''),
                                   reply_markup=kb_select_session(mode, is_select=False))

    if type(res) == str:
        await add_log(f"[{user_id}] успешно завершил решение [{mode}]")
        return await callback.answer(res, show_alert=True)

    text_msg, len_answers, correct_answer, current, _ = res
    kb = kb_inline_testing(mode, len_answers, correct_answer, current, is_studying=is_studying)
    log_text = f"[{user_id}] отвечает на вопросы mode [{mode}]"

    if is_exam:
        res = await failed_the_exam(user_id)
        if res:
            user_answer_res = res if type(res) == str else "Экзамен не сдан. Вы допустили 3 ошибки."
            if type(res) != str:
                user_answer_res = "Экзамен уже завершен." if await end_session(user_id, 103) else user_answer_res
            text_msg = await get_stats(user_id)
            kb = kb_select_session(mode, is_select=False)
            await callback.answer(text=user_answer_res, show_alert=True)
            text_msg += "\n\nЭкзамен не сдан!"
            log_text = f"[{user_id}] завалил экзамен."

    await add_log(log_text)
    try:
        await bot.send_message(user_id, text_msg, reply_markup=kb)
    except TelegramRetryAfter:
        await callback.answer(text="Сработал АНТИФЛУД! Подождите 5 минут и продолжайте решение.", show_alert=True)
    else:
        await callback.answer(text=user_answer_res)



def register_callback_handlers(dp: Dispatcher):
    """Регистратор обработчиков inline-сообщений"""
    dp.callback_query.register(cmd_select_session, F.data.startswith("session_"))
    dp.callback_query.register(cmd_inline_testing, F.data.startswith("test_"))
