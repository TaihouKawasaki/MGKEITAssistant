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

#DEEPSEEK API CONFIG 
DEEPSEEK_API_KEY = "sk-587336cfed46439b92aee62d87a51faf"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

#CONTENT FILTER
import re
import string
import math
class SimpleContentFilter:
    def __init__(self):
        """Инициализация фильтра рандомного текста"""
        
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
        
        # Базовые проверки ссылок
        self.spam_patterns = [
            r'http[s]?://\S+',
            r'www\.\S+',
            r'\S+@\S+\.\S+',
        ]
        
        # Раскладки клавиатуры
        self.keyboard_layouts = {
            'qwerty': [
                'qwertyuiop',
                'asdfghjkl',
                'zxcvbnm'
            ],
            'azerty': [
                'azertyuiop',
                'qsdfghjklm',
                'wxcvbn'
            ],
            'йцукен': [
                'йцукенгшщзхъ',
                'фывапролджэ',
                'ячсмитьбю'
            ]
        }
        
        # Частые паттерны клавиш
        self.key_patterns = [
            # Горизонтальные строки
            'qwerty', 'asdfgh', 'zxcvbn',
            'йцукен', 'фывапр', 'ячсмит',
            
            # Вертикальные столбцы
            'qaz', 'wsx', 'edc', 'rfv', 'tgb', 'yhn', 'ujm', 'ik', 'ol', 'p',
            'йфя', 'цыч', 'увс', 'кам', 'епн', 'рго', 'илт', 'ош', 'щб', 'зж', 'хъ',
            
            # Диагонали
            'qasw', 'wsde', 'edfr', 'rfgt', 'tghy', 'yhui', 'ujik', 'ikol', 'olp',
            
            # Комбинации
            '123', '456', '789', 'qwe', 'rty', 'asd', 'fgh', 'zxc', 'vbn',
            'йцу', 'фыв', 'ячс', '123456', 'qwerty', 'йцукен',
        ]
        
        
        self.common_words = self._load_common_words()
        
        # Пороговые значения
        self.thresholds = {
            'min_length': 6,        
            'max_repetition': 0.3,    
            'min_entropy': 2.5,       
            'keyboard_score': 0.6,    
            'pattern_match': 0.7,     
        }
    
    def _load_common_words(self) -> set[str]:
        """Загружает список самых частых слов"""
        common_words = {
            'я', 'ты', 'он', 'она', 'оно', 'мы', 'вы', 'они', 'меня', 'тебя',
            'его', 'её', 'нас', 'вас', 'их', 'себя', 'мой', 'твой', 'наш',
            'ваш', 'свой', 'это', 'то', 'всё', 'все', 'такой', 'такая',
            'такое', 'такие', 'который', 'которая', 'которое', 'которые',
            'какой', 'какая', 'какое', 'какие', 'кто', 'что', 'где', 'куда',
            'когда', 'почему', 'зачем', 'как', 'сколько', 'чей', 'чья',
            'чьё', 'чьи', 'нет', 'да', 'не', 'ни', 'ну', 'вот', 'уж', 'даже',
            'просто', 'прямо', 'почти', 'только', 'лишь', 'именно', 'даже',
            'уже', 'ещё', 'опять', 'снова', 'вдруг', 'почти', 'совсем',
            'очень', 'слишком', 'весьма', 'чрезвычайно', 'привет', 'пока',
            'здравствуйте', 'до', 'свидания', 'спасибо', 'пожалуйста',
            'извините', 'простите', 'здорово', 'хорошо', 'плохо', 'нормально',
            'отлично', 'прекрасно', 'ужасно', 'замечательно', 'класс',
            
            
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her',
            'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their', 'mine',
            'yours', 'hers', 'ours', 'theirs', 'this', 'that', 'these',
            'those', 'who', 'what', 'where', 'when', 'why', 'how', 'which',
            'whose', 'whom', 'yes', 'no', 'not', 'very', 'too', 'so', 'just',
            'only', 'really', 'quite', 'pretty', 'rather', 'almost', 'even',
            'still', 'already', 'yet', 'again', 'never', 'always', 'often',
            'sometimes', 'usually', 'rarely', 'seldom', 'hello', 'hi', 'bye',
            'goodbye', 'thanks', 'thank', 'please', 'sorry', 'excuse',
            'welcome', 'well', 'good', 'bad', 'okay', 'fine', 'great',
            'excellent', 'terrible', 'awesome', 'cool', 'nice',
        }
        return common_words
    
    async def should_block(self, text: str) -> tuple[bool, str]:
        """Простая проверка - возвращает (блокировать, причина)"""
        if not text or len(text) < 2:
            return False, ""
        
        # 1. Проверка длины
        if len(text) > 500:
            return True, "Сообщение слишком длинное"
        
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
        
        # 5. Проверка на символьный спам
        if re.search(r'[!?]{4,}', text):
            return True, "Слишком много восклицательных или вопросительных знаков"
        
        # 6. Проверка на однотипные символы
        if re.search(r'(.)\1{4,}', text):
            char_match = re.search(r'(.)\1{4,}', text)
            if char_match:
                repeated_char = char_match.group(1)
                if repeated_char != '.':
                    return True, "Обнаружены повторяющиеся символы"
        
        # 7. Проверка на злоупотребление специальными символами
        special_chars = re.findall(r'[@#$%^&*()_+=|<>~{}[\]:;"/\\]', text)
        if len(special_chars) > len(text) * 0.3:
            return True, "Слишком много специальных символов"
        
        # 8. Проверка на рандомный текст
        is_random, reason = self.is_random_text(text)
        if is_random:
            return True, f"Рандомный текст: {reason}"
        
        return False, ""
    
    def is_random_text(self, text: str) -> tuple[bool, str]:
        """
        Определяет, является ли текст рандомным.
        Возвращает (является_ли_рандомным, причина)
        """
        if not text or len(text.strip()) < self.thresholds['min_length']:
            return False, "Слишком короткий текст"
        
        text_lower = text.lower()
        clean_text = re.sub(r'[^\w\s]', '', text_lower)
        text_no_spaces = re.sub(r'\s+', '', clean_text)
        
        # Быстрые проверки
        checks = [
            self._check_repetitive_patterns,
            self._check_keyboard_patterns,
            self._check_low_entropy,
            self._check_vowel_consonant_ratio,
            self._check_no_meaningful_words,
            self._check_keyboard_rows,
            self._check_adjacent_keys,
            self._check_character_variety,
        ]
        
        for check_func in checks:
            is_random, reason = check_func(text_lower, clean_text, text_no_spaces)
            if is_random:
                return True, reason
        
        return False, "Нормальный текст"
    
    def _check_repetitive_patterns(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка повторяющихся паттернов"""
        if len(text_no_spaces) < 8:
            return False, ""
        
        # Проверка циклических паттернов (abcabc)
        for pattern_len in range(2, 5):
            if len(text_no_spaces) >= pattern_len * 2:
                pattern = text_no_spaces[:pattern_len]
                repeats = 0
                for i in range(0, len(text_no_spaces) - pattern_len + 1, pattern_len):
                    if text_no_spaces[i:i+pattern_len] == pattern:
                        repeats += 1
                if repeats >= 3:
                    return True, f"Циклический паттерн '{pattern}'"
        
        # Проверка повторяющихся символов
        char_counts = {}
        for char in text_no_spaces:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        most_common = max(char_counts.values(), default=0)
        if most_common / len(text_no_spaces) > self.thresholds['max_repetition']:
            return True, "Слишком много повторяющихся символов"
        
        return False, ""
    
    def _check_keyboard_patterns(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка паттернов клавиатуры"""
        if len(text_no_spaces) < 4:
            return False, ""
        
        # Проверка известных паттернов
        for pattern in self.key_patterns:
            if pattern in text_no_spaces:
                if not self._is_in_common_word(text_lower, pattern):
                    return True, f"Паттерн клавиш '{pattern}'"
        
        return False, ""
    
    def _check_low_entropy(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка низкой энтропии (информационной плотности)"""
        if len(text_no_spaces) < 10:
            return False, ""
        
        entropy = self._calculate_entropy(text_no_spaces)
        
        if entropy < self.thresholds['min_entropy']:
            return True, f"Низкая энтропия ({entropy:.2f})"
        
        return False, ""
    
    def _calculate_entropy(self, text: str) -> float:
        """Вычисляет информационную энтропию текста"""
        if not text:
            return 0
        
        # Подсчет частот символов
        char_counts = {}
        for char in text:
            char_counts[char] = char_counts.get(char, 0) + 1
        
        entropy = 0
        text_len = len(text)
        
        for count in char_counts.values():
            probability = count / text_len
            entropy -= probability * math.log2(probability)
        
        return entropy
    
    def _check_vowel_consonant_ratio(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка соотношения гласных/согласных"""
        if len(text_no_spaces) < 8:
            return False, ""
        
        vowels_en = 'aeiou'
        vowels_ru = 'аеёиоуыэюя'
        vowels = vowels_en + vowels_ru
        
        consonants_en = 'bcdfghjklmnpqrstvwxyz'
        consonants_ru = 'бвгджзйклмнпрстфхцчшщ'
        consonants = consonants_en + consonants_ru
        

        vowel_count = sum(1 for c in text_no_spaces if c in vowels)
        consonant_count = sum(1 for c in text_no_spaces if c in consonants)
        
        total_letters = vowel_count + consonant_count
        
        if total_letters < 6:
            return False, ""
        
        vowel_ratio = vowel_count / total_letters
        
        
        if vowel_ratio < 0.2 or vowel_ratio > 0.8:
            return True, f"Ненормальное соотношение гласных/согласных ({vowel_ratio*100:.1f}% гласных)"
        
        return False, ""
    
    def _check_no_meaningful_words(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка отсутствия осмысленных слов"""
        words = re.findall(r'\b\w+\b', clean_text)
        
        if not words:
            return False, ""
        
        
        meaningful_count = 0
        for word in words:
            if self._is_meaningful_word(word):
                meaningful_count += 1
        
        meaningful_ratio = meaningful_count / len(words)
        
        if meaningful_ratio < 0.2: 
            return True, "Слишком мало осмысленных слов"
        
        return False, ""
    
    def _is_meaningful_word(self, word: str) -> bool:
        """Определяет, является ли слово осмысленным"""
        if len(word) <= 2:
            # Короткие слова проверяем по словарю
            return word.lower() in self.common_words
        
        # Длинные слова считаем осмысленными, если они не выглядят как рандом
        # Проверяем наличие гласных
        vowels = 'aeiouаеёиоуыэюя'
        has_vowels = any(char in vowels for char in word.lower())
        
        # Проверяем наличие повторяющихся паттернов
        if len(word) >= 4:
            # Ищем повторяющиеся триграммы
            trigrams = {}
            for i in range(len(word) - 2):
                trigram = word[i:i+3].lower()
                trigrams[trigram] = trigrams.get(trigram, 0) + 1
            
            # Если какая-то триграмма повторяется
            for count in trigrams.values():
                if count > 1:
                    return False  # Вероятно, рандомный паттерн
        
        return has_vowels  # Слово с гласными считаем осмысленным
    
    def _check_keyboard_rows(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка строк клавиатуры"""
        if len(text_no_spaces) < 6:
            return False, ""
        
        # Проверяем все раскладки
        for layout_name, rows in self.keyboard_layouts.items():
            for row in rows:
                if len(row) < 3:
                    continue
                
                # Проверяем, состоит ли текст в основном из символов одной строки
                row_chars = set(row)
                text_chars = set(text_no_spaces)
                
                # Если более 80% символов из одной строки
                common_chars = text_chars.intersection(row_chars)
                if len(common_chars) / max(len(text_chars), 1) > 0.8:
                    # Проверяем, что это не часть нормального слова
                    if not self._is_in_common_word(text_lower, row):
                        return True, f"Символы из строки '{row}' ({layout_name})"
        
        return False, ""
    
    def _check_adjacent_keys(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка рядом стоящих клавиш"""
        if len(text_no_spaces) < 4:
            return False, ""
        
        # Координаты клавиш на QWERTY
        qwerty_coords = {
            '1': (0, 0), '2': (0, 1), '3': (0, 2), '4': (0, 3), '5': (0, 4), '6': (0, 5), '7': (0, 6), '8': (0, 7), '9': (0, 8), '0': (0, 9),
            'q': (1, 0), 'w': (1, 1), 'e': (1, 2), 'r': (1, 3), 't': (1, 4), 'y': (1, 5), 'u': (1, 6), 'i': (1, 7), 'o': (1, 8), 'p': (1, 9),
            'a': (2, 0), 's': (2, 1), 'd': (2, 2), 'f': (2, 3), 'g': (2, 4), 'h': (2, 5), 'j': (2, 6), 'k': (2, 7), 'l': (2, 8),
            'z': (3, 0), 'x': (3, 1), 'c': (3, 2), 'v': (3, 3), 'b': (3, 4), 'n': (3, 5), 'm': (3, 6),
        }
        
        # Координаты клавиш на ЙЦУКЕН
        ycuken_coords = {
            'ё': (0, 0), '1': (0, 1), '2': (0, 2), '3': (0, 3), '4': (0, 4), '5': (0, 5), '6': (0, 6), '7': (0, 7), '8': (0, 8), '9': (0, 9), '0': (0, 10), '-': (0, 11), '=': (0, 12),
            'й': (1, 0), 'ц': (1, 1), 'у': (1, 2), 'к': (1, 3), 'е': (1, 4), 'н': (1, 5), 'г': (1, 6), 'ш': (1, 7), 'щ': (1, 8), 'з': (1, 9), 'х': (1, 10), 'ъ': (1, 11),
            'ф': (2, 0), 'ы': (2, 1), 'в': (2, 2), 'а': (2, 3), 'п': (2, 4), 'р': (2, 5), 'о': (2, 6), 'л': (2, 7), 'д': (2, 8), 'ж': (2, 9), 'э': (2, 10),
            'я': (3, 0), 'ч': (3, 1), 'с': (3, 2), 'м': (3, 3), 'и': (3, 4), 'т': (3, 5), 'ь': (3, 6), 'б': (3, 7), 'ю': (3, 8), '.': (3, 9),
        }
        
        all_coords = {**qwerty_coords, **ycuken_coords}
        
        # Анализируем последовательности
        for i in range(len(text_no_spaces) - 3):
            sequence = text_no_spaces[i:i+4]
            
            # Проверяем, что все символы есть в координатах
            if all(char in all_coords for char in sequence):
                coords = [all_coords[char] for char in sequence]
                
                # Проверяем, являются ли клавиши соседними
                is_adjacent = True
                for j in range(len(coords) - 1):
                    row1, col1 = coords[j]
                    row2, col2 = coords[j + 1]
                    
                    # Расстояние между клавишами
                    row_diff = abs(row1 - row2)
                    col_diff = abs(col1 - col2)
                    
                    # Клавиши считаются соседними если они рядом по горизонтали, вертикали или диагонали
                    if row_diff > 1 or col_diff > 1:
                        is_adjacent = False
                        break
                
                if is_adjacent:
                    return True, "Рядом стоящие клавиши"
        
        return False, ""
    
    def _check_character_variety(self, text_lower: str, clean_text: str, text_no_spaces: str) -> tuple[bool, str]:
        """Проверка разнообразия символов"""
        if len(text_no_spaces) < 10:
            return False, ""
        
        # Уникальные символы
        unique_chars = len(set(text_no_spaces))
        unique_ratio = unique_chars / len(text_no_spaces)
        
        # Нормальный текст имеет разнообразие символов
        if unique_ratio < 0.3:
            return True, f"Слишком мало уникальных символов ({unique_chars}/{len(text_no_spaces)})"
        
        # Проверяем группы символов
        groups = {
            'letters': string.ascii_letters + 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя',
            'digits': string.digits,
            'symbols': string.punctuation + ' '
        }
        
        # Считаем символы по группам
        group_counts = {group: 0 for group in groups}
        
        for char in text_lower:
            for group_name, group_chars in groups.items():
                if char in group_chars:
                    group_counts[group_name] += 1
                    break
        
        # Проверяем, не состоит ли текст в основном из одной группы
        for group_name, count in group_counts.items():
            if count / len(text_lower) > 0.9:
                return True, f"Текст состоит в основном из {group_name}"
        
        return False, ""
    
    def _is_in_common_word(self, text: str, pattern: str) -> bool:
        """Проверяет, является ли паттерн частью часто используемого слова"""
        allowed_patterns_in_words = {
            'qwerty': ['qwerty'],
            'asdf': ['asdf'],
            'йцукен': ['йцукен'],
            'фыва': ['фыва'],
            'password': ['password'],
            'keyboard': ['keyboard'],
            'test': ['test'],
            'hello': ['hello'],
        }
        
        # Проверяем весь текст на наличие слов с паттернами
        for word, patterns in allowed_patterns_in_words.items():
            if word in text.lower():
                for p in patterns:
                    if p == pattern:
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
    await message.answer('''MGKEITAssistant ver1.1.1 indev build 25Dec01Getsu01p42
Github project of the bot in case I abandon this project: https://github.com/TaihouKawasaki/MGKEITAssistant
Made by: TaihouKawasaki, NaokiEijiro

🤖 **Интегрирован AI-помощник DeepSeek**
🛡️ **Система фильтрации контента активна**''')
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
        ai_response = await call_deepseek_api(message.text, user_id)
        
        has_profanity_in_response, _ = await profanity_filter.contains_profanity(ai_response)
        if has_profanity_in_response:
            ai_response = "⚠️ Извините, я не могу сгенерировать ответ на этот запрос из-за политики контента."
        await message.answer(ai_response)
        
        with open('userrequests.txt', 'a') as file:
            file.write(f'At {datetime.datetime.now()} AI response sent to user {user_id}\n')
        
    except Exception as e:
        print(f"Ошибка обработки AI сообщения: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса. Попробуйте еще раз.")


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
    row = []
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
    try:
        mcreqjson = mcreq.json()['buildings']
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")
        return
    
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
    gpreq = requests.post(COL_URL + gp, headers={"Authorization": API_KEY}, json={"building": usrmc, "limit": 500})
    if gpreq.status_code != 200:
        await message.answer(f"Ошибка при получении данных. Код ответа: {gpreq.status_code}, Сообщение: {gpreq.text}")
        return
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
    await state.set_state(ChoiceStates.SELECTING_BUILDINGS) 
    
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
    data = await state.get_data()
    print("Current state data before timetable:", data)
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
        # Если прошло проверку - отправляем в AI
        await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
        with open ('userrequests.txt', 'a') as file:
            file.write(f'At {datetime.datetime.now()} this text was sent to AI: "{message.text}" \n')
        try:
            # Вызов DeepSeek API
            response = await call_deepseek_api(message.text, message.from_user.id)
            await message.answer(response)
            
        except Exception as e:
            await message.answer("❌ Произошла ошибка при обработке запроса. Попробуйте позже.")
            print(f"AI processing error: {e}")
            
    else:
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
