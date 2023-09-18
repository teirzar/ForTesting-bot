def get_token() -> str:
    """Функция читает файл key.txt в директории private.
    Внести в него свой токен!"""
    with open('private/key.txt', 'r') as file:
        token = file.readline()
        return token
