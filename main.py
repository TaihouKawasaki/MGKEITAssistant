import asyncio
from aiogram import *
from os import *
from aiogram.filters import Command
from aiogram.types import Message

dp = Dispatcher()

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello World!")


# Run the bot
async def main() -> None:
    bot = Bot(token="7767007017:AAFAVDnC4ToW3G4PlaO7TTKDk6ZaNxFRwXM")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
