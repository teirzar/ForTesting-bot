from aiogram.types import Message
from aiogram import Bot, Dispatcher
from keyboadrs import kb_main_menu, kb_profile_menu
from aiogram import F


async def cmd_main_menu(message: Message, bot: Bot):
    """Обработчик клавиатуры kb_main_menu"""
    await bot.send_message(message.from_user.id, f'Главное меню.', reply_markup=kb_main_menu())


async def cmd_mode_selection(message: Message, bot: Bot):
    """Функция для запуска определенного режима"""
    match message.text:
        case "Режим изучения":
            ...
        case "Обычный режим":
            ...
        case "Режим экзамена":
            ...
        case "Режим марафона":
            ...
        case "Случайный режим":
            ...
        case "Работа над ошибками":
            ...


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
    dp.message.register(cmd_mode_selection, F.text == "Работа над ошибками")

    dp.message.register(cmd_profile_menu, F.text == "Мой профиль")


