import asyncio
from aiogram import *
from os import *
from aiogram.filters import Command
from aiogram.types import Message


#Initilization of the requests handler module
dp = Dispatcher()

#Async functions answering to the main commands
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Бот запущен!")

@dp.message(Command("help"))
async def command_start_handler(message: Message) -> None:
    await message.answer('''/start - Запускает бота
/help - Вывод всех комманд и их назначения
/ver - Вывод нынешней версии бота, а так же ответвтвенных за разработку данного бота
/jobseeking - Выдача Телеграм канала "Навигатор трудоустроиства МГКЭИТ" ''')

@dp.message(Command("ver"))
async def command_start_handler(message: Message) -> None:
    await message.answer('''MGKEITAssistant ver0.1 indev build 25Nov04Ka12a36
Github project of the bot: https://github.com/TaihouKawasaki/MGKEITAssistant
Made by: TaihouKawasaki, Klabautermann-von-Uten, YarMinator''')

@dp.message(Command("jobseeking"))
async def command_start_handler(message: Message) -> None:
    await message.answer("https://t.me/+hh0SWOc-tK80YjMy")


#Indev Build classification: Last 2 digits of the year + first 3 symbols of the month + 2 digit date + day of the week + Hours + AM\PM + Minutes
#Monday - Getsu
#Tuesday - Ka
#Wednesday - Sui
#Thursday - Moku
#Friday - Kin
#Saturday - Do
#Sunday - Nichi

#echoing user's text
@dp.message()
async def echo(message: types.Message):
    await message.answer(text=message.text)


#Bot initilization and it's API key
async def main() -> None:
    bot = Bot(token="7767007017:AAFAVDnC4ToW3G4PlaO7TTKDk6ZaNxFRwXM")
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())
