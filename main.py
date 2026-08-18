import asyncio
from editor_manager import EditorManager

manager = EditorManager()

async def main():
    async for message in manager.run():
        print(message)

if __name__ == "__main__":
    asyncio.run(main())