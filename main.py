import asyncio

from dotenv import load_dotenv

from database.init_database import init_database

load_dotenv()

async def main():
    init_database()
    

if __name__ ==  "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

