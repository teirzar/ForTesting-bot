from aiogram.utils.keyboard import ReplyKeyboardBuilder


def kb_main_menu():
    """Основная клавиатура главного меню"""
    kb = ReplyKeyboardBuilder()

    kb.button(text="Мой профиль")
    kb.button(text="Режим изучения")
    kb.button(text="Обычный режим")
    kb.button(text="Режим экзамена")
    kb.button(text="Режим марафона")
    kb.button(text="Случайный режим")
    kb.button(text="Работа над ошибками")
    kb.adjust(1, 2, 2, 2)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Выберите режим")


def kb_profile_menu():
    """Клавиатура меню пользователя"""
    kb = ReplyKeyboardBuilder()

    kb.button(text="Изменить имя")
    kb.button(text="Изменить табельный номер")
    kb.button(text="Перемешивание вариантов ответа")
    kb.button(text="Главное меню")

    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True, input_field_placeholder="Выберите желаемое")

