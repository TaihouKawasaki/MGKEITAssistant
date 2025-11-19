# Import main libraries for bot
import asyncio
from aiogram import *
from os import *
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# Import libraries for Yandex.Forms API
import json
import sys
import requests
# Import libs for MGKEIT API
import datetime
import time
#Initilization of the requests handler module
dp = Dispatcher()

#Async functions answering to the main commands
@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer('''Бот запущен! Вот список комманд:
/start - Запускает бота
/help - Вывод всех комманд и их назначения | вызов основной клавиатуры бота
/jobseeking - Выдача Телеграм канала "Навигатор трудоустроиства МГКЭИТ" 
/ver - Вывод нынешней версии бота, а так же ответвтвенных за разработку данного бота
/doc - Запрос документов у МГКЭИТ
/feedback - Обратная связь МГКЭИТ
/timetable - Расписание занятий на сегодня''')
    kb = ReplyKeyboardMarkup()
    kb.add(KeyboardButton('/help'))
    kb.add(KeyboardButton('/jobseeking'))
    kb.add(KeyboardButton('/ver'))
    kb.add(KeyboardButton('/doc'))
    kb.add(KeyboardButton('/feedback'))
    kb.add(KeyboardButton('/timetable'))
    await bot.send_message(chat_id = message.from_user.id,
                           text="test",
                           parse_mode = "HTML",
                           reply_markup=kb)
    

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
    await message.answer('''MGKEITAssistant ver0.1 indev build 25Nov17Getsu09a00
Github project of the bot in case I abandon this project: https://github.com/TaihouKawasaki/MGKEITAssistant
Made by: TaihouKawasaki''')

#Indev Build classification: Last 2 digits of the year + first 3 symbols of the month + 2 digit date + day of the week + Hours + AM\PM + Minutes
#Monday - Getsu
#Tuesday - Ka
#Wednesday - Sui
#Thursday - Moku
#Friday - Kin
#Saturday - Do
#Sunday - Nichi


# Implementing Yandex.Forms API for feedback
# Yandex API Docs: https://yandex.ru/support/forms/ru/api-ref/surveys/events_v1_views_frontend_submit_form_view
# Abandoned for now
yaurl = 'https://api.forms.yandex.net/v1/surveys/69117f7949af47ef77e765ba/form'
myobj = {'id':'69117f7949af47ef77e765ba'}
req = requests.get(url = yaurl, params = myobj)
@dp.message(Command("feedback"))
async def command_start_handler(message: Message) -> None:
    print(req.text)
    await message.answer(req.text)

#Implementing mgkeit.space API
# mgkeit.space API Docs: https://mgkeit.space/developers
colurl = "https://api.mgkeit.space/api/v1"
tt = "/timetable"
gp = "/groups"
mc = "/buildings"
usrgp = "1КС-1-11-25"
usrmc = ""
curweekday = datetime.datetime.today().weekday()
api = 'Bearer mgk_live_t6tio7hb3o7im43hnupj2gcuozuf7zfqsxgelpw4acyzep4qlziq'
mcreq = requests.post(url = colurl+mc, headers = {'Authorization': api})
mcjson = mcreq.json()

@dp.message(Command("buildings"))
async def command_start_handler(message: Message) -> None:
    mcreq = requests.post(url = colurl+mc, headers = {'Authorization': api})
    await message.answer("Производим запрос филиалов колледжа")
    time.sleep(1)
    convmcreqcode = str(mcreq)
    await message.answer(convmcreqcode)
    mcreqjson = mcreq.json()
    mcreqjson = mcreqjson['buildings']
    nummc = len(mcreqjson)
    i = 1
    for i in range(nummc):
        istr = i + 1
        istr = str(istr)
        await message.answer(istr + ". " + mcreqjson[i])
        i = i + 1
 

    
@dp.message(Command("groups"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Производим запрос групп")

@dp.message(Command("timetable"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Производим запрос расписания на сегодня")
    ttreq = requests.post(url = colurl+tt, headers = {'Authorization': api}, json = {'group': usrgp, 'day': curweekday})
    convttreqcode = str(ttreq)
    ttreqjson = ttreq.json()
    weekday = ttreqjson['data'][0]['day_name']
    await message.answer(convttreqcode)
    await message.answer(f"День недели: {weekday}")
    reqvalid = True
    i = 0
    while reqvalid == True:
            kind = ttreqjson['data'][0]['units'][i]['kind']
            if kind == "pair":
                display_number = ttreqjson['data'][0]['units'][i]['display_number']
                start = ttreqjson['data'][0]['units'][i]['start']
                subject = ttreqjson['data'][0]['units'][i]['subject']
                end = ttreqjson['data'][0]['units'][i]['end']
                teher = ttreqjson['data'][0]['units'][i]['teacher']
                rum = ttreqjson['data'][0]['units'][i]['room']
                await message.answer(f'''Тип занятия {kind}
Номер занятия {display_number}
Название предмета: {subject}
Преподаватель: {teher}
Кабинет: {rum}
Начало: {start}
Конец: {end}''')
                reqvalid = True
            else:
                break
            i = i + 1

    
#Bot initilization and it's API key
async def main() -> None:
    bot = Bot(token="7767007017:AAFAVDnC4ToW3G4PlaO7TTKDk6ZaNxFRwXM")
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())




