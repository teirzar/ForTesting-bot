from config import users


async def get_users() -> list:
    """Возвращает ID всех пользователей"""
    res = users.print_table('id')
    if res:
        return [user[0] for user in res]
    return []


async def register(user_id, name, personnel_number) -> None:
    """Функция для регистрации пользователя в базе данных"""
    users.write('id', 'name', 'personnel_number', values=f'{user_id}, "{name}", {personnel_number}')
