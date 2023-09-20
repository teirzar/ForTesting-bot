from aiogram.utils.keyboard import InlineKeyboardBuilder


def kb_select_session(mode):
    """Клавиатура для выбора сессии или для подтверждения создания новой сессии"""
    ikb = InlineKeyboardBuilder()

    ikb.button(text="Продолжить решать", callback_data="321")
    ikb.button(text="Начать заново", callback_data="321")
    ikb.adjust(1, 1)

    return ikb.as_markup()


def kb_inline_testing(len_answers, correct_answer, is_studying=False):
    """Клавиатура тестирования"""
    ikb = InlineKeyboardBuilder()

    for i in range(len_answers):
        if i == correct_answer:
            ikb.button(text=str(i + 1) + "+", callback_data="123")
            continue
        ikb.button(text=str(i + 1), callback_data="123")

    if is_studying:
        ikb.button(text="Показать верный ответ", callback_data="123")

    ikb.adjust(len_answers, 1)
    return ikb.as_markup()
