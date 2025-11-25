# Import main libraries for bot
import asyncio
from aiogram import *
import os
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
# Import libs for MGKEIT API
import datetime
import time
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
import mariadb
import json
import sys
import requests




#Initilization of the requests handler module
dp = Dispatcher()

# Создание списка кнопок с удобочитаемыми названиями
buttons = [
    [KeyboardButton(text="Старт"), KeyboardButton(text="Помощь")],  # Пользователь видит понятные надписи
    [KeyboardButton(text="Работа"), KeyboardButton(text="Документы")],
    [KeyboardButton(text="Версия"), KeyboardButton(text="Обратная связь")],
    [KeyboardButton(text="Расписание"), KeyboardButton(text="Филиалы")],
    [KeyboardButton(text="Группа")] 
]

# Создание клавиатуры с передачей списка кнопок
commands_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer('''Бот запущен!
Для первичной настройки бота выберите филиал колледжа командой, затем группу.''', reply_markup=commands_keyboard)
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /start was used \n')

@dp.message(Command("help"))
async def command_help_handler(message: Message) -> None:
    help_text = '''Список команд:
Старт - запускает бота
Помощь - выводит список команд и их назначение
Работа - выдача Телеграм-канала "Навигатор трудоустройства МГКЭИТ"
Документы - запрашивает документы у МГКЭИТ
Версия - показывает версию бота и разработчиков
Обратная связь - отправляет отзыв разработчикам
Расписание - расписание занятий на сегодня
Филиалы - выбор филиала колледжа
Группа - выбор учебной группы'''
    await message.answer(help_text, reply_markup=commands_keyboard)
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /help was used \n')
    
@dp.message(Command("jobseeking"))
async def command_jobseeking_handler(message: Message) -> None:
    await message.answer("https://t.me/+hh0SWOc-tK80YjMy")
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /jobseeking was used \n')
    
@dp.message(Command("doc"))
async def command_doc_handler(message: Message) -> None:
    await message.answer("Пока бот не может запросить справку, сделайте это самостоятельно по ссылке: https://mgkeit.space/documents")
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /doc was used \n')
 
    
@dp.message(Command("ver"))
async def command_ver_handler(message: Message) -> None:
    await message.answer('''MGKEITAssistant ver0.1 indev build 25Nov21Kin07p00
Github project of the bot in case I abandon this project: https://github.com/TaihouKawasaki/MGKEITAssistant
Made by: TaihouKawasaki, NaokiEijiro''')
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /ver was used \n')
#Indev Build classification: Last 2 digits of the year + first 3 symbols of the month + 2 digit date + day of the week + Hours + AM\PM + Minutes

#Monday - Getsu

#Tuesday - Ka

#Wednesday - Sui

#Thursday - Moku

#Friday - Kin

#Saturday - Do

#Sunday - Nichi



#/feedback
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'MGKEITFeedback'
}
@dp.message(Command("feedback"))
async def command_feedback_handler(message: Message) -> None:
    await message.answer("Ведется работа над добавлением обратной связи, пока используйте данную ссылку: mgkeit.space")
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /feedback was used \n')



    
#Implementing mgkeit.space API
# mgkeit.space API Docs: https://mgkeit.space/developers
colurl = "https://api.mgkeit.space/api/v1"
tt = "/timetable"
gp = "/groups"
mc = "/buildings"
curweekday = datetime.datetime.today().weekday()
api = 'Bearer mgk_live_t6tio7hb3o7im43hnupj2gcuozuf7zfqsxgelpw4acyzep4qlziq'

@dp.message(Command("buildings"))
async def command_buildings_handler(message: Message) -> None:
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

    
    #await message.answer(    
    global usrmc
    usrmc = mcreqjson[4]
    print(usrmc)
    with open('Buildingslogs.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /buildings was used\n')

    
@dp.message(Command("groups"))
async def command_groups_handler(message: Message) -> None:
    try:
        await message.answer("Производим запрос групп")
        gpreq = requests.post(url = colurl+gp, headers = {'Authorization': api}, json = {'building': usrmc, 'limit': 500})
        gpreqjson = gpreq.json()
        gpreqjson = gpreqjson['groups']
        numgp = len(gpreqjson)
        print(numgp)
        i = 1
        for i in range(numgp):
            istr = i + 1
            istr = str(istr)
            await message.answer(istr + ". " + gpreqjson[i])
            i = i + 1

        
    except NameError:
        await message.answer("Филиал не выбран, пропишите /buildings для выбора филиала")
    global usrgp
    usrgp = "1КС-1-11-25"
    with open('groupslogs.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /groups was used \n')

@dp.message(Command("timetable"))
async def command_timetable_handler(message: Message) -> None:
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
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /timetable was used \n')
    
# Обработчики кнопок 
@dp.message(lambda msg: msg.text == "Старт")
async def button_start_handler(message: Message) -> None:
    await command_start_handler(message)

@dp.message(lambda msg: msg.text == "Помощь")
async def button_help_handler(message: Message) -> None:
    await command_help_handler(message)

@dp.message(lambda msg: msg.text == "Работа")
async def button_jobseeking_handler(message: Message) -> None:
    await command_jobseeking_handler(message)

@dp.message(lambda msg: msg.text == "Документы")
async def button_doc_handler(message: Message) -> None:
    await command_doc_handler(message)

@dp.message(lambda msg: msg.text == "Версия")
async def button_ver_handler(message: Message) -> None:
    await command_ver_handler(message)

@dp.message(lambda msg: msg.text == "Обратная связь")
async def button_feedback_handler(message: Message) -> None:
    await command_feedback_handler(message)

@dp.message(lambda msg: msg.text == "Расписание")
async def button_timetable_handler(message: Message) -> None:
    await command_timetable_handler(message)

@dp.message(lambda msg: msg.text == "Филиалы")
async def button_buildings_handler(message: Message) -> None:
    await command_buildings_handler(message)

@dp.message(lambda msg: msg.text == "Группа")
async def button_groups_handler(message: Message) -> None:
    await command_groups_handler(message)


# Logging other user inputs
@dp.message()
async def usrinput(message: types.Message):
    await message.answer("Кастомный запрос пользователя принят, он будет обработан в дальнейшем. Спасибо вам!")
    with open('userrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} was detected custom user input, contents: "{message.text}" \n')    
    
#Bot initilization and it's API key
async def main() -> None:
    bot = Bot(token="7767007017:AAFAVDnC4ToW3G4PlaO7TTKDk6ZaNxFRwXM")
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())
