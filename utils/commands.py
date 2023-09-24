from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    """Установка команд кнопки меню"""
    commands = [BotCommand(command='menu', description='Главное меню'),
                BotCommand(command='profile', description="Профиль"),
                BotCommand(command='help', description='Помощь')]
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
