from aiogram.types import Message
from aiogram import Bot, Dispatcher
from keyboadrs import kb_main_menu
from aiogram import F


async def cmd_main_menu(message: Message, bot: Bot):
    """Обработчик клавиатуры kb_main_menu"""
    await bot.send_message(message.from_user.id, f'Главное меню.', reply_markup=kb_main_menu())


def register_message_handlers(dp: Dispatcher):
    """Регистратор обработчиков сообщений"""
    dp.message.register(cmd_main_menu, F.text == "/menu")
