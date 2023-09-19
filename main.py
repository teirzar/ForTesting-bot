import logging
import sys
import asyncio


if __name__ == "__main__":
    from functions import main

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Завершено по желанию пользователя")
    except:
        print("Завершено из-за ошибки")
