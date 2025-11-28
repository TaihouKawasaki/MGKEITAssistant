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
#import mariadb
import json
import sys
import requests
import logging
from typing import List
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

dp = Dispatcher()
# Роутер для обработки команд
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Класс состояний для хранения текущих выборов
class ChoiceStates(StatesGroup):
    SELECTING_BUILDING = State()  # Этап выбора филиала
    SELECTING_GROUP = State()     # Этап выбора группы

# Создание списка кнопок с удобочитаемыми названиями
buttons = [
    [KeyboardButton(text="🚀 Старт"), KeyboardButton(text="❓ Помощь")],
    [KeyboardButton(text="🛠 Работа"), KeyboardButton(text="📄 Документы")],
    [KeyboardButton(text="🔧 Версия"), KeyboardButton(text="✉️ Обратная связь")],
    [KeyboardButton(text="📆 Расписание"), KeyboardButton(text="🏫 Филиалы")],
    [KeyboardButton(text="👥 Группа")] 
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
/start - запускает бота
/help - выводит список команд и их назначение
/jobseeking - выдача Телеграм-канала "Навигатор трудоустройства МГКЭИТ"
/doc - запрашивает документы у МГКЭИТ
/ver - показывает версию бота и разработчиков
/feedback - отправляет отзыв разработчикам
/timetable - расписание занятий на сегодня
/buildings - выбор филиала колледжа
/groups - выбор учебной группы'''
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
    await message.answer('''MGKEITAssistant ver1.0 indev build 25Nov28Kin03p37
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

dp.include_router(router)

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
mc = "/buildings"
gp = "/groups"
tt = "/timetable"
COL_URL = "https://api.mgkeit.space/api/v1"
API_KEY = "Bearer mgk_live_t6tio7hb3o7im43hnupj2gcuozuf7zfqsxgelpw4acyzep4qlziq"
curweekday = datetime.datetime.today().weekday()


# Вспомогательная функция для генерации inline-клавиатуры
def generate_inline_buttons(data):
    """Создание inline-клавиатуры с кнопками в две колонки."""
    buttons = []
    row = []  # Однострочный массив кнопок
    for idx, item in enumerate(data, start=1):
        callback_data = f"select_{item}"
        button = InlineKeyboardButton(text=f"{idx}. {item}", callback_data=callback_data)
        row.append(button)
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Обработчик команды /buildings
@router.message(Command("buildings"))
async def buildings_command_handler(message: Message, state: FSMContext):
    # Запрашиваем данные через API
    mcreq = requests.post(COL_URL + mc, headers={"Authorization": API_KEY})
    if mcreq.status_code != 200:
        await message.answer(f"Ошибка при получении данных. Код ответа: {mcreq.status_code}, Сообщение: {mcreq.text}")
        return
    
    await message.answer("Производим запрос филиалов колледжа...")
    
    # Парсим JSON и получаем список филиалов
    try:
        mcreqjson = mcreq.json()['buildings']
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        return
    
    # Генерируем inline-клавиатуру
    markup = generate_inline_buttons(mcreqjson)
    await message.answer("Выберите филиал:", reply_markup=markup)

# Обработчик нажатия на кнопку филиала
@router.callback_query(F.data.startswith("select_"))
async def handle_building_selection(query: CallbackQuery, state: FSMContext):
    # Извлекаем выбранный филиал из callback_data
    _, chosen_filial = query.data.split("_", maxsplit=1)
    
    # Сохраняем выбранный филиал в состоянии
    await state.update_data(building=chosen_filial)
    
    # Переходим в состояние выбора группы
    await state.set_state(ChoiceStates.SELECTING_GROUP)
    
    # Отвечаем пользователю и сохраняем выбор
    await query.message.edit_text(f"Вы выбрали филиал: {chosen_filial}")
    print(chosen_filial)
    with open('Buildingslogs.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} user chose building: {chosen_filial}\n')


@dp.message(Command("buildings"))
async def buildings_command_redirect(message: Message, state: FSMContext) -> None:
    await buildings_command_handler(message, state)
    
# Обработчик команды /groups
@router.message(Command("groups"))
async def groups_command_handler(message: Message, state: FSMContext):
    # Чтение выбранного филиала из состояния
    data = await state.get_data()
    usrmc = data.get("building")
    
    if not usrmc:
        await message.answer("Сначала выберите филиал с помощью команды /buildings.")
        return
    
    await message.answer("Производим запрос групп...")
    
    # Отправляем запрос на сервер с выбранным филиалом
    gpreq = requests.post(COL_URL + gp, headers={"Authorization": API_KEY}, json={"building": usrmc, "limit": 500})
    
    if gpreq.status_code != 200:
        await message.answer(f"Ошибка при получении данных. Код ответа: {gpreq.status_code}, Сообщение: {gpreq.text}")
        return
    
    # Парсим JSON и получаем список групп
    gpreqjson = gpreq.json()
    gpreqjson = gpreqjson['groups']
    
    # Генерируем inline-клавиатуру с группами
    markup = generate_inline_buttons(gpreqjson)
    await message.answer("Выберите группу:", reply_markup=markup)

# Обработчик нажатия на кнопку группы
@router.callback_query(F.data.startswith("select_"), ChoiceStates.SELECTING_GROUP)
async def handle_group_selection(query: CallbackQuery, state: FSMContext):
    # Извлекаем выбранную группу из callback_data
    _, chosen_group = query.data.split("_", maxsplit=1)
    
    # Сохраняем выбранную группу под ключом "group"
    await state.update_data(group=chosen_group)
    
    # Завершаем этап выбора группы
    await state.set_state(ChoiceStates.SELECTING_BUILDINGS)  # Устанавливаем отсутствие активных состояний
    
    # Отвечаем пользователю и сохраняем выбор
    await query.message.edit_text(f"Вы выбрали группу: {chosen_group}")
    print(chosen_group)
    with open('Groupslogs.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} user chose group: {chosen_group}\n')

@dp.message(Command("groups"))
async def groups_command_redirect(message: Message, state: FSMContext) -> None:
    await groups_command_handler(message, state)
# Обработчик команды /timetable
@router.message(Command("timetable"))
async def timetable_command_handler(message: Message, state: FSMContext):
    # Читаем данные состояния
    data = await state.get_data()
    print("Current state data before timetable:", data)

    # Читаем выбранную группу из состояния
    usrgp = data.get("building")
    
    if not usrgp:
        await message.answer("Сначала выберите группу с помощью команды /groups.")
        return
    try:
        await message.answer("Производим запрос расписания на сегодня")
        ttreq = requests.post(url=COL_URL + tt, headers={'Authorization': API_KEY}, json={'group': usrgp, 'day': curweekday})
        convttreqcode = str(ttreq)
        ttreqjson = ttreq.json()
        weekday = ttreqjson['data'][0]['day_name']
        await message.answer(convttreqcode)
        await message.answer(f"День недели: {weekday}")
        reqvalid = True
        i = 0
        while reqvalid:
            kind = ttreqjson['data'][0]['units'][i].get('kind')
            if kind == "pair":
                display_number = ttreqjson['data'][0]['units'][i]['display_number']
                start = ttreqjson['data'][0]['units'][i]['start']
                subject = ttreqjson['data'][0]['units'][i]['subject']
                end = ttreqjson['data'][0]['units'][i]['end']
                teacher = ttreqjson['data'][0]['units'][i]['teacher']
                room = ttreqjson['data'][0]['units'][i]['room']
                await message.answer(f'''
Тип занятия: {kind}
Номер занятия: {display_number}
Предмет: {subject}
Преподаватель: {teacher}
Кабинет: {room}
Время: {start}-{end}
''')
                reqvalid = True
            else:
                break
            i += 1
    except KeyError:
         await message.answer("Сначала выберите группу с помощью команды /groups.")
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /timetable was used\n')

        
@dp.message(Command("timetable"))
async def timetable_command_redirect(message: Message, state: FSMContext) -> None:
    await timetable_command_handler(message, state)
# Включаем роутер в диспетчер

    
# Обработчики кнопок 
@dp.message(lambda msg: msg.text == "🚀 Старт")
async def button_start_handler(message: Message) -> None:
    await command_start_handler(message)

@dp.message(lambda msg: msg.text == "❓ Помощь")
async def button_help_handler(message: Message) -> None:
    await command_help_handler(message)

@dp.message(lambda msg: msg.text == "🛠 Работа")
async def button_jobseeking_handler(message: Message) -> None:
    await command_jobseeking_handler(message)

@dp.message(lambda msg: msg.text == "📄 Документы")
async def button_doc_handler(message: Message) -> None:
    await command_doc_handler(message)

@dp.message(lambda msg: msg.text == "🔧 Версия")
async def button_ver_handler(message: Message) -> None:
    await command_ver_handler(message)

@dp.message(lambda msg: msg.text == "✉️ Обратная связь")
async def button_feedback_handler(message: Message) -> None:
    await command_feedback_handler(message)

@dp.message(lambda msg: msg.text == "📆 Расписание")
async def button_timetable_handler(message: Message, state: FSMContext) -> None:
    await timetable_command_handler(message, state)

@dp.message(lambda msg: msg.text == "🏫 Филиалы")
async def button_buildings_handler(message: Message, state: FSMContext) -> None:
    await buildings_command_handler(message, state)

@dp.message(lambda msg: msg.text == "👥 Группа")
async def button_groups_handler(message: Message, state: FSMContext) -> None:
    await groups_command_handler(message, state)


# Logging other user inputs
@dp.message()
async def usrinput(message: types.Message):
    await message.answer("Кастомный запрос пользователя принят, он будет обработан в дальнейшем. Спасибо вам!")
    with open('userrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} was detected custom user input, contents: "{message.text}" \n')    
    
#Bot initilization and it's API key
async def main() -> None:
    bot = Bot(token="5455458009:AAGSa9Qq2enzAXjbjxA9nHcCPpmvfreqYkk")
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())
