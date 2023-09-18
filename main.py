import logging
import sys
import asyncio


if __name__ == "__main__":
    from functions import main

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
