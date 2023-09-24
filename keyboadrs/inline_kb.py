from aiogram.utils.keyboard import InlineKeyboardBuilder


def kb_select_session(mode, is_select=True):
    """Клавиатура для выбора сессии или для подтверждения создания новой сессии"""
    ikb = InlineKeyboardBuilder()

    if is_select:
        ikb.button(text="Продолжить решать", callback_data=f"session_continue_{mode}")
    ikb.button(text="Начать заново", callback_data=f"session_new_{mode}")
    ikb.adjust(1, 1)

    return ikb.as_markup()


def kb_inline_testing(mode, len_answers, correct_answer, question, is_studying=False, show=False):
    """Клавиатура тестирования"""
    ikb = InlineKeyboardBuilder()

    for i in range(len_answers):
        if i == correct_answer:
            ikb.button(text=str(i + 1) + (' ✅' if show else ''), callback_data=f"test_{mode}__{question}_correct")
            continue
        ikb.button(text=str(i + 1) + (' ❌' if show else ''), callback_data=f"test_{mode}__{question}_mistake")

    if is_studying:
        ikb.button(text=("Скрыть" if show else "Показать") + " верный ответ",
                   callback_data=f"test_{mode}_{'hide' if show else 'show'}_{question}_open")

    if str(mode) != "106":
        ikb.button(text="Завершить решение досрочно", callback_data=f'test_{mode}___end')

    ikb.adjust(len_answers, 1, 1)
    return ikb.as_markup()
