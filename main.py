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
import aiohttp

#DEEPSEEK API CONFIG (для работы с ИИ)
DEEPSEEK_API_KEY = "sk-587336cfed46439b92aee62d87a51faf"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

#SIMPLE CONTENT FILTER
import re

class SimpleContentFilter:
    def __init__(self):
        # Минимальный набор самых частых плохих слов
        self.bad_patterns = [
            r'\b[бb][лl][яyаa]\w*', 
            r'\b[пp][иi][з3z]\w*', 
            r'\b[еe][б6b]\w*',
            r'\b[хx][уy]\w*',
            r'\b[сc][уy][кk]\w*',
            r'\b[мm][уy][дd][аa][кk]\w*',
            r'\b[гg][оo0][нn][дd][оo0][нn]\w*',
            r'\b[дd][еe][б6b][иi][лl]\w*',
            r'\b[иi][дd][иi][оo0][тt]\w*',
        ]
        
        # Базовые проверки
        self.spam_patterns = [
            r'http[s]?://\S+',
            r'www\.\S+',
            r'\S+@\S+\.\S+',
        ]
        
        # Спам-паттерны
        self.spam_detection = [
            r'(.)\1{5,}',  # 6+ одинаковых символов подряд
            r'[!?.,]{4,}',  # 4+ знаков препинания подряд
        ]
    
    async def should_block(self, text: str) -> tuple[bool, str]:
        """Простая проверка - возвращает (блокировать, причина)"""
        if not text or len(text) < 2:
            return False, ""
        
        # 1. Проверка длины
        if len(text) > 500:
            return True, "Сообщение слишком длинное"
        if len(text) < 10:
            return True, "Сообщение слишком короткое"
        
        text_lower = text.lower()
        
        # 2. Проверка ссылок
        for pattern in self.spam_patterns:
            if re.search(pattern, text_lower):
                return True, "Обнаружены ссылки"
        
        # 3. Проверка плохих слов
        for pattern in self.bad_patterns:
            if re.search(pattern, text_lower):
                return True, "Обнаружена нецензурная лексика"
        
        # 4. Проверка КАПС ЛОК
        if len(re.findall(r'[A-ZА-Я]', text)) / max(len(text), 1) > 0.6:
            return True, "Слишком много заглавных букв"
        
        # 5. Проверка на повторяющиеся символы (спам)
        for pattern in self.spam_detection:
            try:
                if re.search(pattern, text):
                    return True, "Обнаружен спам (повторяющиеся символы)"
            except re.error as e:
                # Логируем ошибку в паттерне, но продолжаем работу
                print(f"Ошибка в паттерне: {pattern} - {e}")
                continue
        
        # 6. Проверка на чередующиеся символы (типа "абабаб", "121212")
        if await self._check_alternating_patterns(text):
            return True, "Обнаружен спам (чередующиеся символы)"
        
        # 7. Проверка на циклические паттерны
        if await self._check_cyclic_patterns(text):
            return True, "Обнаружен циклический спам"
        
        # 8. Проверка на последовательности
        if await self._check_sequential_patterns(text):
            return True, "Обнаружена последовательность символов"
        
        # 9. Проверка на слишком много одинаковых слов
        words = re.findall(r'\b\w+\b', text_lower)
        if len(words) > 5:
            word_counts = {}
            for word in words:
                if len(word) > 2:
                    word_counts[word] = word_counts.get(word, 0) + 1
            
            for word, count in word_counts.items():
                if count > 5 and len(word) > 3:
                    return True, f"Слишком много повторений слова '{word[:10]}...'"
        
        # 10. Проверка на символьный спам
        if re.search(r'[!?]{4,}', text):
            return True, "Слишком много восклицательных или вопросительных знаков"
        
        # 11. Проверка на однотипные символы
        if re.search(r'(.)\1{4,}', text):
            char_match = re.search(r'(.)\1{4,}', text)
            if char_match:
                repeated_char = char_match.group(1)
                if repeated_char != '.':
                    return True, "Обнаружены повторяющиеся символы"
        
        # 12. Проверка на минимальную уникальность
        if len(text) > 50:
            unique_chars = len(set(text.lower()))
            if unique_chars < 5:
                return True, "Слишком мало уникальных символов (возможный спам)"
        
        # 13. Проверка на злоупотребление специальными символами
        special_chars = re.findall(r'[@#$%^&*()_+=|<>~{}[\]:;"/\\]', text)
        if len(special_chars) > len(text) * 0.3:
            return True, "Слишком много специальных символов"
        
        # 14. Проверка на повтор символов с пробелами (простая версия)
        if await self._check_repeated_chars_with_spaces(text):
            return True, "Обнаружен спам с повторяющимися символами"
        
        return False, ""
    
    async def _check_alternating_patterns(self, text: str) -> bool:
        """Проверка на чередующиеся символы - упрощенная версия"""
        text_no_spaces = re.sub(r'\s+', '', text.lower())
        
        if len(text_no_spaces) < 6:
            return False
        
        # Проверяем простые случаи вручную
        # 1. Проверка на "абабаб" или "121212" (2 символа)
        if len(text_no_spaces) >= 4:
            # Берем первые 4 символа
            sample = text_no_spaces[:4]
            # Проверяем, чередуются ли они
            if len(set(sample)) <= 2:  # Если только 1-2 уникальных символа
                # Проверяем паттерн из 2 символов
                pattern = sample[:2]
                # Проверяем, повторяется ли этот паттерн
                repeats = 0
                for i in range(0, len(text_no_spaces) - 1, 2):
                    if i + 1 < len(text_no_spaces) and text_no_spaces[i:i+2] == pattern:
                        repeats += 1
                if repeats >= 3:  # Если паттерн повторяется 3+ раза
                    return True
        
        # 2. Проверка на "абвабв" (3 символа)
        if len(text_no_spaces) >= 6:
            sample = text_no_spaces[:3]
            # Если это 3 уникальных символа, проверяем повторение
            if len(set(sample)) == 3:
                # Проверяем, повторяется ли этот паттерн
                repeats = 0
                for i in range(0, len(text_no_spaces) - 2, 3):
                    if i + 2 < len(text_no_spaces) and text_no_spaces[i:i+3] == sample:
                        repeats += 1
                if repeats >= 2:  # Если паттерн повторяется 2+ раза
                    return True
        
        return False
    
    async def _check_cyclic_patterns(self, text: str) -> bool:
        """Проверка на циклические паттерны (типа 'abcabcabc')"""
        text_no_spaces = re.sub(r'\s+', '', text.lower())
        
        if len(text_no_spaces) < 6:
            return False
        
        # Проверяем возможные длины циклов (2-5 символов)
        for cycle_len in range(2, 6):
            if len(text_no_spaces) >= cycle_len * 2:  # Хотя бы 2 повторения
                # Берем предполагаемый паттерн из начала строки
                possible_pattern = text_no_spaces[:cycle_len]
                
                # Строим ожидаемую строку с двумя повторениями
                expected = possible_pattern * 2
                
                # Проверяем, начинается ли текст с двух повторений паттерна
                if text_no_spaces.startswith(expected):
                    # Также проверяем остаток текста
                    remaining = text_no_spaces[len(expected):]
                    if remaining.startswith(possible_pattern) or len(remaining) == 0:
                        return True
        
        return False
    
    async def _check_sequential_patterns(self, text: str) -> bool:
        """Проверка на последовательности символов - упрощенная версия"""
        text_no_spaces = re.sub(r'\s+', '', text)
        
        if len(text_no_spaces) < 5:
            return False
        
        # Проверяем последовательности цифр
        digits_match = re.search(r'\d{5,}', text_no_spaces)
        if digits_match:
            digits = digits_match.group()
            # Проверяем, являются ли цифры последовательными
            if len(digits) >= 5:
                # Преобразуем в список чисел
                numbers = [int(d) for d in digits[:5]]
                # Проверяем последовательность вперед
                is_forward = all(numbers[i] + 1 == numbers[i+1] for i in range(len(numbers)-1))
                # Проверяем последовательность назад
                is_backward = all(numbers[i] - 1 == numbers[i+1] for i in range(len(numbers)-1))
                
                if is_forward or is_backward:
                    return True
        
        # Проверяем буквенные последовательности (латиница)
        letters_match = re.search(r'[a-zA-Z]{5,}', text_no_spaces)
        if letters_match:
            letters = letters_match.group().lower()
            if len(letters) >= 5:
                # Преобразуем в коды
                codes = [ord(c) for c in letters[:5]]
                is_forward = all(codes[i] + 1 == codes[i+1] for i in range(len(codes)-1))
                is_backward = all(codes[i] - 1 == codes[i+1] for i in range(len(codes)-1))
                
                if is_forward or is_backward:
                    return True
        
        # Проверяем русские буквенные последовательности
        ru_letters_match = re.search(r'[а-я]{5,}', text_no_spaces.lower())
        if ru_letters_match:
            letters = ru_letters_match.group()
            if len(letters) >= 5:
                # Русский алфавит: а=1072, б=1073, в=1074, ...
                codes = [ord(c) for c in letters[:5]]
                is_forward = all(codes[i] + 1 == codes[i+1] for i in range(len(codes)-1))
                is_backward = all(codes[i] - 1 == codes[i+1] for i in range(len(codes)-1))
                
                if is_forward or is_backward:
                    return True
        
        return False
    
    async def _check_repeated_chars_with_spaces(self, text: str) -> bool:
        """Проверка на повтор символов с пробелами (типа 'а а а а')"""
        # Убираем все кроме букв и цифр
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        # Убираем множественные пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        words = clean_text.split()
        if len(words) < 4:
            return False
        
        # Проверяем, состоит ли текст из повторяющихся коротких слов/символов
        # Считаем уникальные слова
        unique_words = set(words)
        if len(unique_words) <= 2 and len(words) >= 4:
            # Если всего 1-2 уникальных слова, но много повторений
            for word in unique_words:
                if len(word) <= 2 and words.count(word) >= 4:
                    return True
        
        # Проверяем паттерны типа "а б а б"
        if len(words) >= 4:
            # Проверяем паттерн из 2 слов
            if len(words) >= 4:
                pattern = words[:2]
                repeats = 0
                for i in range(0, len(words) - 1, 2):
                    if i + 1 < len(words) and words[i:i+2] == pattern:
                        repeats += 1
                if repeats >= 2:  # Если паттерн повторяется 2+ раза
                    return True
        
        return False
    
dp = Dispatcher()
router = Router()
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
content_filter = SimpleContentFilter()

# Хранилище для DeepSeek контекста
user_conversations = {}

#DEEPSEEK API FUNCTION (функции ИИ)
async def call_deepseek_api(message: str, user_id: int) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    if user_id not in user_conversations:
        user_conversations[user_id] = []
    
    user_conversations[user_id].append({"role": "user", "content": message})
    
    if len(user_conversations[user_id]) > 8:
        user_conversations[user_id] = user_conversations[user_id][-8:]
    
    data = {
        "model": "deepseek-chat",
        "messages": user_conversations[user_id],
        "temperature": 0.7,
        "max_tokens": 2048,
        "stream": False
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=30) as response:
                if response.status == 200:
                    result = await response.json()
                    ai_response = result['choices'][0]['message']['content']
                    
                    user_conversations[user_id].append({"role": "assistant", "content": ai_response})
                    
                    print(f"Успешный ответ от API для пользователя {user_id}")
                    return ai_response
                else:
                    error_text = await response.text()
                    print(f"API Error: {response.status} - {error_text}")
                    return "✅ Спасибо за запрос."
                    
    except asyncio.TimeoutError:
        print("Timeout при обращении к DeepSeek API")
        return "⏰ Превышено время ожидания ответа от AI. Попробуйте еще раз."
    except Exception as e:
        print(f"Request error: {e}")
        return "❌ Произошла ошибка при обработке запроса. Попробуйте позже."

# Класс состояний для хранения текущих выборов
class ChoiceStates(StatesGroup):
    SELECTING_BUILDING = State()  # Этап выбора филиала
    SELECTING_GROUP = State()     # Этап выбора группы

# Создание списка кнопок с удобочитаемыми названиями
buttons = [
    [KeyboardButton(text="🚀 Старт"), KeyboardButton(text="❓ Помощь")],
    [KeyboardButton(text="👥 Группа"), KeyboardButton(text="🏫 Филиалы")],
    [KeyboardButton(text="📆 Расписание"), KeyboardButton(text="🛠 Работа")],
    [KeyboardButton(text="🔧 Версия"), KeyboardButton(text="📄 Документы")],
    [KeyboardButton(text="✉️ Обратная связь"), KeyboardButton(text="🤖 AI Помощник")],
    [KeyboardButton(text="🆕 Новый диалог")]
]

# Создание клавиатуры с передачей списка кнопок
commands_keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer('''Бот запущен!
Для первичной настройки бота выберите филиал колледжа командой, затем группу.

🤖 **Доступен AI-помощник** - используйте кнопку "AI Помощник" для общения с искусственным интеллектом!''', reply_markup=commands_keyboard)
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
/groups - выбор учебной группы
/ai - общение с AI-помощником (DeepSeek)
/new - начать новый диалог с AI'''
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
    await message.answer('''MGKEITAssistant ver1.1 indev build 25Dec01Getsu11a02
Github project of the bot in case I abandon this project: https://github.com/TaihouKawasaki/MGKEITAssistant
Made by: TaihouKawasaki, NaokiEijiro

🤖 **Интегрирован AI-помощник DeepSeek**
🛡️ **Система фильтрации контента активна**''')
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /ver was used \n')

# AI Помощник команды
@dp.message(Command("ai"))
async def command_ai_handler(message: Message) -> None:
    ai_help_text = '''
🤖 **AI Помощник DeepSeek**

Теперь вы можете общаться с искусственным интеллектом! Просто напишите любой вопрос или задачу.

🛡️ **Фильтрация контента:** Сообщения проверяются на нецензурную лексику.

💡 **Совет:** Используйте "Новый диалог" чтобы очистить историю разговора.
'''
    await message.answer(ai_help_text, reply_markup=commands_keyboard)
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /ai was used \n')

@dp.message(Command("new"))
async def command_new_handler(message: Message) -> None:
    user_id = message.from_user.id
    if user_id in user_conversations:
        user_conversations[user_id] = []
        await message.answer("🆕 История диалога с AI очищена. Начинаем новый разговор!")
    else:
        await message.answer("✅ История диалога уже пуста. Можете начинать общение!")
    with open('usercommandrequests.txt', 'a') as file:
        file.write(f'At {datetime.datetime.now()} command /new was used \n')

# Обработчик AI сообщений
async def handle_ai_message(message: Message):
    """Обработка сообщений для AI-помощника"""
    user_id = message.from_user.id
    
    # Проверка на нецензурную лексику
    has_profanity, reason = await profanity_filter.contains_profanity(message.text)
    
    if has_profanity:
        warning_text = f"""
🚫 **Сообщение заблокировано системой фильтрации**

**Причина:** {reason}

Пожалуйста, переформулируйте ваше сообщение без нарушений правил.
"""
        await message.answer(warning_text)
        
        with open('userrequests.txt', 'a') as file:
            file.write(f'At {datetime.datetime.now()} AI message blocked for user {user_id}. Reason: {reason}\n')
        return
    
    # Показываем индикатор набора
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        # Получаем ответ от DeepSeek API
        ai_response = await call_deepseek_api(message.text, user_id)
        
        # Проверка ответа от AI
        has_profanity_in_response, _ = await profanity_filter.contains_profanity(ai_response)
        if has_profanity_in_response:
            ai_response = "⚠️ Извините, я не могу сгенерировать ответ на этот запрос из-за политики контента."
        
        # Отправляем ответ пользователю
        await message.answer(ai_response)
        
        with open('userrequests.txt', 'a') as file:
            file.write(f'At {datetime.datetime.now()} AI response sent to user {user_id}\n')
        
    except Exception as e:
        print(f"Ошибка обработки AI сообщения: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса. Попробуйте еще раз.")

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

@dp.message(lambda msg: msg.text == "🤖 AI Помощник")
async def button_ai_handler(message: Message) -> None:
    await command_ai_handler(message)

@dp.message(lambda msg: msg.text == "🆕 Новый диалог")
async def button_new_handler(message: Message) -> None:
    await command_new_handler(message)

#Обработка сообщений с фильтром
@dp.message()
async def handle_all_messages(message: Message):
    # Если сообщение не команда и не кнопка - проверяем фильтром
    if (message.text and 
        not message.text.startswith('/') and 
        not any(btn.text == message.text for row in buttons for btn in row)):
        
        # Простая проверка фильтром
        should_block, reason = await content_filter.should_block(message.text)
        
        if should_block:
            await message.answer(f"🚫 Сообщение заблокировано: {reason}")
            with open('Bannedmessages.txt', 'a') as file:
                file.write(f'At {datetime.datetime.now()} message blocked: {reason} - "{message.text}" \n')
            return
        
        #with open('userrequests.txt', 'a') as file:
        #   file.write(f'At {datetime.datetime.now()} was detected custom user input, contents: "{message.text}" \n')
        
        # Если прошло проверку - отправляем в AI
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        with open ('userrequests.txt', 'a') as file:
            file.write(f'At {datetime.datetime.now()} this text was sent to AI: "{message.text}" \n')
        try:
            # Ваш вызов DeepSeek API
            response = await call_deepseek_api(message.text, message.from_user.id)
            await message.answer(response)
            
        except Exception as e:
            await message.answer("❌ Произошла ошибка при обработке запроса. Попробуйте позже.")
            print(f"AI processing error: {e}")
            
    else:
        # Логируем команды/кнопки
        with open('userrequests.txt', 'a') as file:
            file.write(f'At {datetime.datetime.now()} command/button: "{message.text}" \n')
    
#Bot initilization and it's API key
async def main() -> None:
    bot = Bot(token="5455458009:AAGSa9Qq2enzAXjbjxA9nHcCPpmvfreqYkk")
    # Проверяем наличие DeepSeek API ключа
    if DEEPSEEK_API_KEY == "ВАШ_DEEPSEEK_API_KEY_ЗДЕСЬ":
        print("❌ ВНИМАНИЕ: Замените DEEPSEEK_API_KEY на реальный ключ!")
    
    print("🤖 Бот запускается...")
    print("🛡️ Простая система фильтрации контента активна")
    print(f"🧠 AI помощник: {'Активен' if DEEPSEEK_API_KEY != 'ВАШ_DEEPSEEK_API_KEY_ЗДЕСЬ' else 'Не настроен'}")
    
    await dp.start_polling(bot)

#loop
if __name__ == "__main__":
    asyncio.run(main())
