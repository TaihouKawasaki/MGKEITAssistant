# Import main libraries for bot
import asyncio
from aiogram import *
from os import *
from aiogram.filters import Command
from aiogram.types import Message
# Import libraries for Yandex.Forms API
from json import *
from sys import *
from requests import *


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
/jobseeking - Выдача Телеграм канала "Навигатор трудоустроиства МГКЭИТ" 
/ver - Вывод нынешней версии бота, а так же ответвтвенных за разработку данного бота
/doc - Запрос документов у МГКЭИТ
/feedback - Обратная связь МГКЭИТ
/timetable - Расписание занятий на сегодня''')

@dp.message(Command("jobseeking"))
async def command_start_handler(message: Message) -> None:
    await message.answer("https://t.me/+hh0SWOc-tK80YjMy")

@dp.message(Command("doc"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Пока бот не может запросить справку, сделайте это самостоятельно по ссылке: https://mgkeit.space/documents")

    
@dp.message(Command("ver"))
async def command_start_handler(message: Message) -> None:
    await message.answer('''MGKEITAssistant ver0.1 indev build 25Nov04Ka09p35
Github project of the bot: https://github.com/TaihouKawasaki/MGKEITAssistant
Made by: TaihouKawasaki, Klabautermann-von-Uten, YarMinator''')

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
    await message.answer("Не распознал комманду, пропишите /help для получения списка комманд.")

# Implementing Yandex.Forms API for feedback
# Yandex API Docs: https://yandex.ru/support/forms/ru/api-ref/surveys/events_v1_views_frontend_submit_form_view
@dp.message(Command("feedback"))
async def command_start_handler(message: Message) -> None:
    await message.answer("TEST")


#Implementing mgkeit.space API
# mgkeit.space API Docs: https://mgkeit.space/developers
@dp.message(Command("timetable"))
async def command_start_handler(message: Message) -> None:
    await message.answer("TEST")



#Bot initilization and it's API key
async def main() -> None:
    bot = Bot(token="7767007017:AAFAVDnC4ToW3G4PlaO7TTKDk6ZaNxFRwXM")
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())

