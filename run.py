import asyncio
from weekly_parasha import root_agent
from dotenv import load_dotenv

load_dotenv()

async def main():
    # Pass input as a simple string or the first positional argument
    async for event in root_agent.run_async("Yitro"):
        print(event)

asyncio.run(main())