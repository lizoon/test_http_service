from routes.additional import plans_performance
from app import *
import asyncio


async def main():
    result = await plans_performance("15.01.2020")
    print(result)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    loop.run_until_complete(main())
