from aiogram import types, Dispatcher
from functions import add_log, register, get_users
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from keyboadrs import kb_main_menu
from aiogram.filters import CommandStart


class SetNamePN(StatesGroup):
    """Машина состояний для установки данных пользователя в базу данных"""
    name = State()
    personnel_number = State()
    letters = "йцукенгшщзхъфывапролджэячсмитьбюёqwertyuiopasdfghjklzxcvbnm"


async def create_new_user(message: types.Message, state: FSMContext):
    text = "Введите свое полное имя:"
    if message.from_user.id in await get_users():
        text = "Вы уже зарегистрированы!\nИзменить данные можно в профиле."
        return await message.answer(text, reply_markup=kb_main_menu())
    await add_log(f"[{message.from_user.id}] начал процедуру регистрации.")
    await message.answer(text)
    await state.set_state(SetNamePN.name)


async def check_name(message: types.Message, state: FSMContext):
    if set(message.text.lower()) - set(SetNamePN.letters):
        await add_log(f"[{message.from_user.id}] неуспешно ввел имя [{message.text}].")
        return await message.reply("Имя должно быть написано буквами русского или латинского алфавита.")
    await state.update_data(name=message.text)
    await add_log(f"[{message.from_user.id}] успешно ввел имя [{message.text}].")
    await message.answer("Введите табельный номер:")
    await state.set_state(SetNamePN.personnel_number)


async def check_personnel_number(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if not message.text.isdigit() or len(message.text) != 5:
        await add_log(f"[{message.from_user.id}] неуспешно ввел табельный номер [{message.text}].")
        return await message.reply("Табельный номер должен состоять из комбинации пяти цифр.")
    await state.update_data(personnel_number=message.text)
    await add_log(f"[{message.from_user.id}] успешно ввел табельный номер [{message.text}].")
    data = await state.get_data()
    name, personnel_number = data.get('name'), data.get('personnel_number')
    message_text = f"Ваше имя: {name}\nВаш табельный номер: {personnel_number}\nРегистрация успешно завершена!"
    await message.answer(message_text, reply_markup=kb_main_menu())
    await register(user_id, name, personnel_number)
    await add_log(f"[{message.from_user.id}] успешная регистрация.")
    await state.clear()


def register_fsm_handlers(dp: Dispatcher):
    """Регистратор обработчиков машины состояний"""
    dp.message.register(create_new_user, CommandStart())
    dp.message.register(check_name, SetNamePN.name)
    dp.message.register(check_personnel_number, SetNamePN.personnel_number)

