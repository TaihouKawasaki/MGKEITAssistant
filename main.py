import asyncio
from aiogram import *
from os import *
from aiogram.filters import Command
from aiogram.types import Message
#Имборт нужных библиотек


#Иницилизация диспачера(модуля обработки запросов)
dp = Dispatcher()

#Ассинхронная функция, отправляющая 'Hello world!' после выполнения комманды /start
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Бот запущен!")

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(text=message.text)




# Иницилизация бота и его API ключа
async def main() -> None:
    bot = Bot(token="7767007017:AAFAVDnC4ToW3G4PlaO7TTKDk6ZaNxFRwXM")
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())

