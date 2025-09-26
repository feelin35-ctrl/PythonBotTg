"""
Исправленная версия main.py с правильными обработчиками DELETE и OPTIONS
"""

from fastapi import FastAPI, HTTPException, Request, Query

from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os, json, time, zipfile, tempfile, shutil, datetime
import telebot
import threading
import uvicorn
import logging

import logging
import logging

# Импорт вспомогательных функций для новой структуры папок
from bot_structure_utils import (
    get_bot_directory,
    get_bot_scenario_file,
    get_bot_config_file,
    get_bot_media_directory,
    get_bot_logs_directory,
    get_bot_backups_directory,
    get_bot_temp_directory,
    create_bot_config as create_user_bot_config,
    update_bot_config,
    save_bot_scenario as save_user_bot_scenario,
    load_bot_scenario as load_user_bot_scenario,
    list_user_bots,
    bot_directory_exists,
    initialize_bot_structure
)

import requests
import hashlib
import hmac
import base64
from cryptography.fernet import Fernet
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

# Импорты архитектуры блоков
from core.block_registry import block_registry
from core.scenario_runner import ScenarioRunner

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Добавим middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"📥 Incoming request: {request.method} {request.url}")
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        logger.info(f"📤 Response status: {response.status_code} for {request.method} {request.url} - Time: {process_time:.2f}s")
        return response
    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ Error processing request {request.method} {request.url} - Time: {process_time:.2f}s - Error: {e}")
        raise

# ✅ Разрешаем запросы с фронта
# Для продакшена можно задать через переменные окружения
import os
allowed_origins = [
    "http://localhost:3001", 
    "http://127.0.0.1:3001", 
    "http://localhost:3000", 
    "http://127.0.0.1:3000", 
    "http://localhost:3002", 
    "http://127.0.0.1:3002", 
    "http://localhost:3003", 
    "http://127.0.0.1:3003", 
    "http://45.150.9.70:8001",
    "http://45.150.9.70",  # Добавляем адрес без порта для продакшена
    "https://your-frontend-domain.com"  # Добавьте сюда домен вашего фронтенда
]

# Добавляем дополнительные origins из переменной окружения
additional_origins = os.getenv("ALLOWED_ORIGINS", "")
if additional_origins:
    allowed_origins.extend(additional_origins.split(","))

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=None,
    expose_headers=[],
    max_age=600,
)

# ========== МОДЕЛИ ==========
class ButtonData(BaseModel):
    label: str

# Добавим модели для аутентификации
class RegisterUserRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginUserRequest(BaseModel):
    username: str
    password: str

class SaveTokenRequest(BaseModel):
    user_id: str
    bot_id: str
    token: str

class UserTokenResponse(BaseModel):
    token: str

class BotDataRequest(BaseModel):
    token: Optional[str] = None

class NodeData(BaseModel):
    label: Optional[str] = None
    url: Optional[str] = None
    images: Optional[List[str]] = None
    buttons: Optional[List[ButtonData]] = None
    condition: Optional[str] = None
    variableName: Optional[str] = None
    method: Optional[str] = None
    payload: Optional[str] = None
    target_node: Optional[str] = None
    onChange: Optional[object] = None
    blockType: Optional[str] = None
    buttonLayout: Optional[str] = None  # Для конфигурации расположения кнопок
    buttonsPerRow: Optional[int] = None  # Количество кнопок в ряду (1-8)
    hideKeyboard: Optional[bool] = None  # Для скрытия клавиатуры
    # Добавляем поля для keyword_processor блока
    keywords: Optional[List[str]] = None
    caseSensitive: Optional[bool] = None
    matchMode: Optional[str] = None

class Node(BaseModel):
    id: str
    type: Optional[str] = None
    data: NodeData
    position: Dict

class Edge(BaseModel):
    id: Optional[str] = None
    source: str
    target: str
    sourceHandle: Optional[str] = None

class Scenario(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    admin_chat_id: Optional[str] = None
    
    class Config:
        # Allow both snake_case and camelCase field names
        @staticmethod
        def alias_generator(field_name: str) -> str:
            # Convert snake_case to camelCase
            components = field_name.split('_')
            return components[0] + ''.join(word.capitalize() for word in components[1:])
        
        populate_by_name = True
        
        # Allow both admin_chat_id and adminChatId
        json_schema_extra = {
            "examples": [
                {
                    "admin_chat_id": "123456789",
                    "adminChatId": "123456789"
                }
            ]
        }


class BotImportData(BaseModel):
    bot_id: str
    scenario: Scenario
    token: str

class TokenData(BaseModel):
    token: str

class AuthData(BaseModel):
    password: str

# ========== НАСТРОЙКИ ==========
BOTS_DIR = "bots"
os.makedirs(BOTS_DIR, exist_ok=True)

# Пароль администратора (в продакшене должен храниться в переменных окружения)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def authenticate_admin(password: str) -> bool:
    """Проверяет пароль администратора"""
    if not ADMIN_PASSWORD:
        logger.warning("Пароль администратора не установлен. В продакшене установите ADMIN_PASSWORD в переменных окружения.")
        return True  # Для разработки разрешаем доступ без пароля
    
    return password == ADMIN_PASSWORD

# Глобальные словари для управления ботами
running_bots = {}
bot_stop_flags = {}
bot_restart_counter = {}  # Счетчик перезапусков для уникальных имен потоков
chat_history = {}  # Храним историю переходов для каждого чата

def load_tokens():
    # Всегда возвращаем пустой словарь, так как токены теперь хранятся в базе данных
    # Эта функция сохраняется для обратной совместимости, но не используется для хранения токенов
    return {}

def save_tokens(tokens):
    # Не сохраняем токены в файл, так как файл токенов больше не используется
    # Все токены теперь хранятся в базе данных
    pass

    pass

def bot_file(bot_id: str, user_id: Optional[str] = None) -> str:
    """Возвращает путь к файлу бота. Если указан user_id, создает подпапку для пользователя."""
    print(f"bot_file вызвана с bot_id={bot_id}, user_id={user_id}")
    
    if user_id:
        # Используем новую структуру папок через bot_structure_utils
        from bot_structure_utils import get_bot_scenario_file
        path = get_bot_scenario_file(user_id, bot_id)
        print(f"Путь к файлу бота с user_id: {path}")
        return path
    else:
        # Используем общую папку для ботов (обратная совместимость)
        path = os.path.join(BOTS_DIR, f"bot_{bot_id}.json")
        print(f"Путь к файлу бота без user_id: {path}")
        return path

def load_scenario(bot_id: str, user_id: Optional[str] = None) -> Scenario:
    # Получаем владельца бота для определения правильного пути
    if not user_id:
        from core.models import UserManager
        user_manager = UserManager()
        user_id = user_manager.get_bot_owner(bot_id)
    
    # Используем только новый путь с user_id
    if user_id:
        file_path = bot_file(bot_id, user_id)
        print(f"Trying to load scenario from user-specific path: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            try:
                print("Opening scenario file...")
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    print(f"Data from file: {data}")
                    print(f"Number of nodes in data: {len(data.get('nodes', []))}")
                    return Scenario(**data)
            except Exception as e:
                logger.error(f"Error loading scenario {bot_id} from user path: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Scenario file not found: {file_path}")
    else:
        print(f"User ID not found for bot {bot_id}")
    
    # Return empty scenario if nothing found
    return Scenario(nodes=[], edges=[])

def save_scenario(bot_id: str, scenario: Scenario, user_id: Optional[str] = None):
    # Если user_id не предоставлен, пытаемся получить его из базы данных
    if not user_id:
        try:
            from core.models import UserManager
            user_manager = UserManager()
            user_id = user_manager.get_bot_owner(bot_id)
        except Exception as e:
            logger.error(f"Ошибка получения владельца бота {bot_id}: {e}")
    
    # Если не можем определить владельца, возвращаем ошибку
    if not user_id:
        logger.error(f"Не удалось определить владельца бота {bot_id} для сохранения сценария")
        raise ValueError(f"Не удалось определить владельца бота {bot_id}")
    
    try:
        file_path = bot_file(bot_id, user_id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(scenario.dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Сценарий сохранен для бота {bot_id} (пользователь: {user_id})")
    except Exception as e:
        logger.error(f"Ошибка сохранения сценария {bot_id}: {e}")
        raise

# ========== API ЭНДПОИНТЫ ==========
@app.get("/")
def read_root():
    return {"message": "Telegram Bot Constructor API"}

def validate_telegram_token(token: str) -> bool:
    """Проверяет валидность токена Telegram"""
    if not token:
        return False
    if ":" not in token:
        return False
    parts = token.split(":")
    if len(parts) != 2:
        return False
    if not parts[0].isdigit() or len(parts[0]) < 5:
        return False
    if len(parts[1]) < 20:
        return False
    return True

def check_token_sync(token: str) -> bool:
    """Синхронная проверка токена Telegram"""
    try:
        print(f"Проверка токена: {'*' * len(token)}")  # Скрыли отображение токена
        
        # Проверяем формат токена
        is_valid_format = validate_telegram_token(token)
        print(f"Формат токена действителен: {is_valid_format}")
        
        if not is_valid_format:
            print(f"Токен не прошел проверку формата")
            return False

        print("Попытка подключения к Telegram API с этим токеном...")
        test_bot = telebot.TeleBot(token)
        bot_info = test_bot.get_me()
        print(f"Успешное подключение! Информация о боте: {bot_info}")
        return True
    except Exception as e:
        print(f"Ошибка при проверке токена: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_telegram_connection():
    """Проверяет возможность подключения к Telegram API"""
    try:
        response = requests.get('https://api.telegram.org', timeout=10)
        return response.status_code == 200
    except:
        return False

def add_to_chat_history(chat_id: int, node_id: str):
    """Добавляет узел в историю чата"""
    if chat_id not in chat_history:
        chat_history[chat_id] = []
    
    # Ограничиваем размер истории (10 последних шагов)
    if len(chat_history[chat_id]) >= 10:
        chat_history[chat_id].pop(0)
    
    # Не добавляем одинаковые узлы подряд
    if not chat_history[chat_id] or chat_history[chat_id][-1] != node_id:
        chat_history[chat_id].append(node_id)
        logger.info(f"🗺️ Добавлено в историю {chat_id}: {node_id}")

def get_previous_node(chat_id: int) -> Optional[str]:
    """Возвращает предыдущий узел из истории"""
    if chat_id not in chat_history or len(chat_history[chat_id]) < 2:
        return None
    
    # Удаляем текущий узел и возвращаем предыдущий
    chat_history[chat_id].pop()  # Удаляем текущий
    previous_node = chat_history[chat_id][-1]  # Берем предыдущий
    logger.info(f"↩️ Возврат к узлу {previous_node} для чата {chat_id}")
    return previous_node

def clear_chat_history(chat_id: int):
    """Очищает историю чата"""
    if chat_id in chat_history:
        del chat_history[chat_id]
        logger.info(f"🧽 Очищена история чата {chat_id}")

def start_telegram_bot(token: str, scenario_data: dict, bot_id: str):
    """Запускает телеграм бота в отдельном потоке"""
    logger.info(f"🔄 Запуск бота {bot_id} с токеном: {'*' * 10}...")  # Скрыли отображение токена

    # Сбрасываем флаг остановки
    bot_stop_flags[bot_id] = False

    max_retries = 3
    retry_delay = 15

    for attempt in range(max_retries):
        try:
            if bot_stop_flags.get(bot_id, True):
                logger.info(f"⏹️ Бот {bot_id} остановлен перед запуском")
                return

            # Проверяем токен
            test_bot = telebot.TeleBot(token)
            bot_info = test_bot.get_me()
            logger.info(f"✅ Токен верный. Бот: @{bot_info.username}")

            # Создаем исполнитель сценария
            scenario_runner = ScenarioRunner(scenario_data)
            if not scenario_runner.nodes_map:
                logger.error("❌ Нет доступных блоков в сценарии!")
                return

            # Создаем настоящего бота
            bot = telebot.TeleBot(token)
                
            logger.info(f"🤖 Бот @{bot_info.username} запускается...")
            
            # Сохраняем экземпляр бота для принудительной остановки
            running_bots[f"{bot_id}_instance"] = bot

            @bot.message_handler(commands=['start', 'help'])
            def handle_start(message):
                try:
                    # Проверяем флаг остановки
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"⏹️ Бот {bot_id} остановлен, игнорируем /start")
                        return
                        
                    logger.info(f"👤 /start от {message.chat.id} - {message.from_user.username}")
                    
                    # Очищаем историю при новом старте
                    clear_chat_history(message.chat.id)
                    
                    # Находим стартовый узел
                    start_node = next((node_id for node_id, block in scenario_runner.nodes_map.items()
                                       if hasattr(block, 'type') and block.type == 'start'), None)
                    if start_node:
                        # Добавляем стартовый узел в историю
                        add_to_chat_history(message.chat.id, start_node)
                        
                        # Запускаем цепочку обработки
                        next_node_id = scenario_runner.process_node(bot, message.chat.id, start_node)
                        while next_node_id:
                            # Проверяем тип следующего узла
                            next_block = scenario_runner.nodes_map.get(next_node_id)
                            if next_block and hasattr(next_block, 'type'):
                                # Добавляем следующий узел в историю
                                add_to_chat_history(message.chat.id, next_node_id)
                                
                                # Если это интерактивные блоки, останавливаем автоматическое выполнение
                                if next_block.type in ['button', 'inline_button', 'input', 'menu']:
                                    # Обрабатываем только этот узел и останавливаемся
                                    scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                    break
                                else:
                                    # Продолжаем для обычных блоков (message, image, condition, etc.)
                                    # Выполняем блок и получаем следующий узел
                                    scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                    # Ищем следующий узел по связям
                                    next_node_id = scenario_runner.get_next_node_id(next_node_id)
                            else:
                                # Если нет информации о типе, обрабатываем как обычный блок
                                add_to_chat_history(message.chat.id, next_node_id)
                                scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                next_node_id = scenario_runner.get_next_node_id(next_node_id)
                    else:
                        bot.send_message(message.chat.id, "🚀 Бот запущен! Напишите что-нибудь.")
                except Exception as e:
                    logger.error(f"❌ Ошибка в /start: {e}")

            # Обработчик команды "Назад"
            @bot.message_handler(func=lambda message: message.text and message.text.lower() in ['/назад', '/back', 'назад', 'back'])
            def handle_back_command(message):
                try:
                    # Проверяем флаг остановки
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"⏹️ Бот {bot_id} остановлен, игнорируем команду Назад")
                        return
                        
                    logger.info(f"↩️ Команда 'Назад' от {message.chat.id}")
                    
                    # Получаем предыдущий узел
                    previous_node_id = get_previous_node(message.chat.id)
                    
                    if previous_node_id:
                        logger.info(f"↩️ Возвращаемся к узлу {previous_node_id}")
                        # Обрабатываем предыдущий узел
                        scenario_runner.process_node(bot, message.chat.id, previous_node_id)
                    else:
                        bot.send_message(message.chat.id, "ℹ️ Нет предыдущих шагов. Используйте /start для начала.")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки команды Назад: {e}")

            # Обработчик пользовательских команд из меню
            @bot.message_handler(func=lambda message: message.text and message.text.startswith('/') and message.text not in ['/start', '/help', '/назад', '/back'])
            def handle_menu_commands(message):
                try:
                    # Проверяем флаг остановки
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"⏹️ Бот {bot_id} остановлен, игнорируем команду")
                        return
                        
                    command = message.text.strip()
                    logger.info(f"📋 Команда меню от {message.chat.id}: {command}")
                    
                    # Ищем блок меню с этой командой
                    for node_id, block in scenario_runner.nodes_map.items():
                        if hasattr(block, 'type') and block.type == 'menu':
                            menu_items = block.node_data.get('data', {}).get('menuItems', [])
                            for item in menu_items:
                                item_command = item.get('command', '').strip()
                                if item_command:
                                    # Приводим к единому формату
                                    if not item_command.startswith('/'):
                                        item_command = f"/{item_command}"
                                    
                                    if item_command == command:
                                        logger.info(f"🎯 Найдена команда {command}, переходим к следующему узлу")
                                        # Находим следующий узел после меню
                                        next_node_id = scenario_runner.get_next_node_id(node_id)
                                        if next_node_id:
                                            # Добавляем в историю
                                            add_to_chat_history(message.chat.id, next_node_id)
                                            scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                        else:
                                            bot.send_message(message.chat.id, f"Команда {command} выполнена!")
                                        return
                    
                    # Если команда не найдена
                    bot.send_message(message.chat.id, f"❓ Неизвестная команда {command}. Используйте /start для начала.")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка обработки команды: {e}")

            # Обработчик callback-запросов (inline-кнопки)
            @bot.callback_query_handler(func=lambda call: True)
            def handle_callback_query(call):
                try:
                    # Проверяем флаг остановки
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"⏹️ Бот {bot_id} остановлен, игнорируем callback")
                        bot.answer_callback_query(call.id, text="Бот остановлен")
                        return
                        
                    logger.info(f"🔘 Callback от {call.from_user.id}: {call.data}")

                    # Ищем блок с inline-кнопками, который соответствует callback_data
                    for node_id, block in scenario_runner.nodes_map.items():
                        if hasattr(block, 'type') and block.type == 'inline_button':
                            buttons = block.node_data.get('data', {}).get('buttons', [])
                            for button in buttons:
                                callback_data = button.get('callbackData',
                                                           f"btn_{hash(button.get('label', '')) % 10000}")
                                if callback_data == call.data:
                                    scenario_runner.handle_inline_button_press(bot, call, node_id, call.data)
                                    return

                    # Если не нашли подходящую кнопку
                    bot.answer_callback_query(call.id, text="Эта кнопка больше не активна")

                except Exception as e:
                    logger.error(f"❌ Ошибка обработки callback: {e}")
                    try:
                        bot.answer_callback_query(call.id, text="Произошла ошибка")
                    except:
                        pass

            @bot.message_handler(func=lambda message: True)
            def handle_all_messages(message):
                try:
                    # Проверяем флаг остановки
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"⏹️ Бот {bot_id} остановлен, игнорируем сообщение")
                        return
                        
                    logger.info(f"💬 Сообщение от {message.chat.id}: {message.text}")

                    # Передаем текст сообщения в сценарий для обработки
                    message_context = {
                        'user_message': message.text,
                        'user_id': message.from_user.id,
                        'username': message.from_user.username
                    }

                    # Проверяем блок обработки ключевых слов
                    keyword_processed = False
                    for node_id, block in scenario_runner.nodes_map.items():
                        if hasattr(block, 'type') and block.type == 'keyword_processor':
                            logger.info(f"🔍 Обработка сообщения с помощью keyword_processor: {message.text}")
                            # Выполняем блок keyword_processor с контекстом сообщения
                            success = block.process(bot, message.chat.id, message.text)
                            if success:
                                keyword_processed = True
                                # Если ключевое слово найдено, продолжаем выполнение сценария
                                # Ищем следующий узел по основной связи
                                next_node_id = scenario_runner.get_next_node_id(node_id)
                                if next_node_id:
                                    scenario_runner.process_node(bot, message.chat.id, next_node_id, **message_context)
                                break  # Прекращаем дальнейшую обработку

                    # Если сообщение было обработано блоком keyword_processor, прекращаем обработку
                    if keyword_processed:
                        return

                    # Проверяем, является ли сообщение нажатием на кнопку
                    for node_id, block in scenario_runner.nodes_map.items():
                        if hasattr(block, 'type') and block.type == 'button':
                            buttons = block.node_data.get('data', {}).get('buttons', [])
                            hide_keyboard = block.node_data.get('data', {}).get('hideKeyboard', False)
                            
                            # Если клавиатура скрыта, проверяем цифровые ответы
                            if hide_keyboard and message.text.isdigit():
                                button_index = int(message.text) - 1  # Пользователь вводит 1-based индекс

                                if 0 <= button_index < len(buttons):
                                    logger.info(f"🔘 Выбран вариант {message.text} (индекс {button_index})")
                                    result = scenario_runner.handle_button_press(bot, message.chat.id, node_id, button_index)
                                    if result:
                                        return
                            
                            # Обычная проверка по тексту кнопки (для не скрытых кнопок)
                            for index, button in enumerate(buttons):
                                if button.get('label') == message.text:
                                    logger.info(f"🔘 Нажата кнопка: {message.text}")
                                    result = scenario_runner.handle_button_press(bot, message.chat.id, node_id, index)
                                    if result:
                                        return
                        
                        # Проверяем inline-кнопки с скрытой клавиатурой
                        elif hasattr(block, 'type') and block.type == 'inline_button':
                            buttons = block.node_data.get('data', {}).get('buttons', [])
                            hide_keyboard = block.node_data.get('data', {}).get('hideKeyboard', False)
                            
                            # Если клавиатура скрыта, проверяем цифровые ответы
                            if hide_keyboard and message.text.isdigit():
                                button_index = int(message.text) - 1  # Пользователь вводит 1-based индекс
                                if 0 <= button_index < len(buttons):
                                    logger.info(f"🔘 Выбран inline-вариант {message.text} (индекс {button_index})")
                                    # Для inline-кнопок используем имитацию callback_data
                                    callback_data = f"btn_{button_index}"
                                    result = scenario_runner.handle_inline_button_press(bot, message, node_id, callback_data)
                                    if result:
                                        return

                        # Проверяем блок обработки естественного языка
                        elif hasattr(block, 'type') and block.type == 'nlp_response':
                            logger.info(f"🧠 Обработка сообщения с помощью NLP: {message.text}")
                            # Выполняем блок NLP с контекстом сообщения
                            result = scenario_runner.process_node(bot, message.chat.id, node_id, **message_context)
                            if result:
                                return

                        # Проверяем блок расписания
                        elif hasattr(block, 'type') and block.type == 'schedule':
                            logger.info(f"📅 Обработка ответа для блока расписания: {message.text}")
                            # Обрабатываем ответ пользователя для блока расписания
                            result = scenario_runner.handle_schedule_response(bot, message.chat.id, node_id, message.text)
                            # Если handle_schedule_response вернул значение (не None), это означает, 
                            # что нужно продолжить выполнение сценария
                            # Если вернул None, это может означать успешное завершение блока расписания
                            # В любом случае, прекращаем дальнейшую обработку сообщения
                            return  # This should prevent the default message from being sent

                    # Если не кнопка и нет NLP блока, отправляем стандартный ответ
                    bot.send_message(message.chat.id, "ℹ️ Используйте /start для начала")

                except Exception as e:
                    logger.error(f"❌ Ошибка обработки сообщения: {e}")
                    try:
                        bot.send_message(message.chat.id, "⚠️ Произошла ошибка при обработке сообщения")
                    except:
                        pass

            # Запускаем polling с проверкой флага остановки
            logger.info("📡 Запускаем polling...")

            while not bot_stop_flags.get(bot_id, True):
                try:
                    # Используем короткие циклы polling для быстрой остановки
                    bot.polling(
                        none_stop=False,  # Не блокируем навсегда
                        interval=1,       # Проверяем каждую секунду
                        timeout=5,        # Короткий timeout
                        long_polling_timeout=5  # Короткий long polling
                    )
                    # Проверяем флаг остановки после каждого цикла
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"🛑 Обнаружен флаг остановки для бота {bot_id}")
                        break
                        
                except Exception as e:
                    if bot_stop_flags.get(bot_id, True):
                        logger.info(f"⏹️ Остановка по флагу в except для бота {bot_id}")
                        break
                    
                    # Проверяем тип ошибки
                    if "409" in str(e) and "getUpdates" in str(e):
                        logger.warning(f"⚠️ Конфликт getUpdates для бота {bot_id}: {e}")
                        logger.info(f"🔄 Ожидание 5 секунд перед повторной попыткой...")
                        time.sleep(5)
                    else:
                        logger.error(f"🔥 Ошибка polling: {e}")
                        logger.info("🔄 Перезапуск polling через 3 секунды...")
                        time.sleep(3)

            logger.info(f"⏹️ Бот {bot_id} остановлен")
            
            # Очищаем экземпляр бота
            bot_instance_key = f"{bot_id}_instance"
            if bot_instance_key in running_bots:
                del running_bots[bot_instance_key]
                logger.info(f"🗑️ Экземпляр бота {bot_id} очищен")
            
            break

        except Exception as e:
            if "Unauthorized" in str(e):
                logger.error("🚫 Неверный токен! Остановка бота.")
                break
            logger.error(f"❌ Ошибка Telegram API: {e}")
            time.sleep(retry_delay)

# ========== ПРАВИЛЬНЫЕ ОБРАБОТЧИКИ DELETE И OPTIONS ==========
@app.options("/api/delete_bot/{bot_id}/")
async def delete_bot_options(bot_id: str):
    """Обработка OPTIONS запроса для удаления бота"""
    response = JSONResponse({"status": "success"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "600"
    return response

@app.delete("/api/delete_bot/{bot_id}/")
def delete_bot(bot_id: str, deleted_by_user_id: Optional[str] = None):
    try:
        print(f"=== DELETE BOT REQUEST ===")
        print(f"bot_id: {bot_id}")
        print(f"deleted_by_user_id: {deleted_by_user_id}")
        
        # Если указан deleted_by_user_id, проверяем, является ли пользователь суперадмином
        is_super_admin = False
        if deleted_by_user_id:
            try:
                from core.models import UserManager
                user_manager = UserManager()
                is_super_admin = user_manager.is_super_admin(deleted_by_user_id)
                print(f"is_super_admin: {is_super_admin}")
            except Exception as e:
                logger.warning(f"Ошибка проверки роли пользователя {deleted_by_user_id}: {e}")
        
        # Получаем владельца бота для определения правильного пути
        from core.models import UserManager
        user_manager = UserManager()
        owner_id = user_manager.get_bot_owner(bot_id)
        print(f"owner_id: {owner_id}")
        
        # Если не можем определить владельца, возвращаем ошибку
        if not owner_id:
            logger.warning(f"Не удалось определить владельца бота {bot_id}")
            response_data = {"status": "error", "message": f"Не удалось определить владельца бота {bot_id}"}
            # Add CORS headers
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
        
        # Если пользователь не является суперадмином, проверяем, что он владелец бота
        if not is_super_admin and deleted_by_user_id != owner_id:
            logger.warning(f"Пользователь {deleted_by_user_id} не имеет прав для удаления бота {bot_id}")
            response_data = {"status": "error", "message": "У вас нет прав для удаления этого бота"}
            # Add CORS headers
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
        
        # Получаем путь к файлу бота с учетом владельца
        file_path = bot_file(bot_id, owner_id)
        print(f"Attempting to delete bot file: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        
        if os.path.exists(file_path):
            # Получаем директорию бота и удаляем всю директорию
            bot_dir = os.path.dirname(file_path)
            if os.path.exists(bot_dir):
                import shutil
                shutil.rmtree(bot_dir)
                logger.info(f"Директория бота {bot_dir} успешно удалена")
            else:
                # Если директория не существует, удаляем только файл сценария
                os.remove(file_path)
            
            # Удаляем токен из базы данных
            try:
                from core.models import UserManager
                user_manager = UserManager()
                deletion_result = user_manager.delete_user_token(owner_id, bot_id)
                if deletion_result:
                    logger.info(f"Токен для бота {bot_id} успешно удален из базы данных")
                else:
                    logger.warning(f"Токен для бота {bot_id} не был найден в базе данных")
            except Exception as e:
                logger.warning(f"Предупреждение: не удалось удалить токен для бота {bot_id} из базы данных: {e}")
            
            # Останавливаем бота если он запущен
            if bot_id in running_bots:
                bot_stop_flags[bot_id] = True
                del running_bots[bot_id]

            # Удаляем информацию о праве собственности на бота из базы данных
            try:
                logger.info(f"Попытка удаления информации о праве собственности на бота {bot_id}")
                deletion_result = user_manager.delete_bot_ownership(bot_id)
                if deletion_result:
                    logger.info(f"Информация о праве собственности на бота {bot_id} успешно удалена из базы данных")
                else:
                    logger.warning(f"Информация о праве собственности на бота {bot_id} не была найдена в базе данных")
            except Exception as e:
                logger.error(f"Ошибка удаления информации о праве собственности на бота {bot_id}: {e}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")

            response_data = {"status": "success", "message": f"Бот {bot_id} успешно удален."}
            # Add CORS headers
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
        else:
            response_data = {"status": "success", "message": f"Бот {bot_id} не найден, возможно уже удален."}
            # Add CORS headers
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "*"
            return response
    except Exception as e:
        logger.error(f"Ошибка удаления бота {bot_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        response_data = {"status": "error", "message": f"Ошибка удаления бота: {str(e)}"}
        # Add CORS headers
        response = JSONResponse(response_data)
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return response

# ========== ОСТАЛЬНЫЕ ЭНДПОИНТЫ ==========
@app.post("/api/import_bot/")
def import_bot(import_data: BotImportData, user_id: Optional[str] = None):
    """Импортирует бота из переданных данных"""
    try:
        bot_id = import_data.bot_id.strip()
        
        # Проверяем, что bot_id не пустой и корректный
        if not bot_id:
            return {"status": "error", "message": "ID бота не может быть пустым"}
        
        # Проверяем, что бот с таким ID не существует
        if os.path.exists(bot_file(bot_id)):
            return {"status": "error", "message": f"Бот с ID '{bot_id}' уже существует"}
        
        # Валидируем токен
        token = import_data.token.strip()
        if not token:
            return {"status": "error", "message": "Токен не может быть пустым"}
        
        if not validate_telegram_token(token):
            return {"status": "error", "message": "Неверный формат токена"}
        
        # Проверяем, что токен работает
        try:
            test_bot = telebot.TeleBot(token)
            bot_info = test_bot.get_me()
            logger.info(f"✅ Токен для импорта верный. Бот: @{bot_info.username}")
        except Exception as e:
            return {"status": "error", "message": f"Токен недействителен: {str(e)}"}
        
        # Валидируем сценарий
        scenario = import_data.scenario
        if not scenario.nodes:
            return {"status": "error", "message": "Сценарий не может быть пустым"}
        
        # Проверяем наличие стартового узла
        has_start_node = any(node.data.blockType == 'start' for node in scenario.nodes)
        if not has_start_node:
            return {"status": "error", "message": "Сценарий должен содержать стартовый узел"}
        
        # Сохраняем сценарий
        logger.info(f"💾 Импортируем сценарий для бота {bot_id}")
        save_scenario(bot_id, scenario)
        
        # Сохраняем токен в базе данных
        logger.info(f"🔑 Импортируем токен для бота {bot_id}")
        if user_id:
            try:
                from core.models import UserManager
                user_manager = UserManager()
                user_manager.save_user_token(user_id, bot_id, token)
                logger.info(f"✅ Токен для бота {bot_id} успешно сохранен в базе данных")
            except Exception as e:
                logger.error(f"❌ Ошибка сохранения токена для бота {bot_id}: {e}")
        else:
            logger.warning(f"⚠️ Не удалось сохранить токен для бота {bot_id} - не указан user_id")
        
        # Register bot ownership if user_id is provided
        if user_id:
            try:
                from core.models import UserManager
                user_manager = UserManager()
                user_manager.register_bot_ownership(user_id, bot_id)
            except Exception as e:
                logger.error(f"Ошибка регистрации права собственности на импортированного бота {bot_id}: {e}")
        
        logger.info(f"✅ Бот {bot_id} успешно импортирован")
        return {
            "status": "success", 
            "message": f"Бот '{bot_id}' успешно импортирован",
            "bot_info": {
                "username": bot_info.username,
                "name": f"{bot_info.first_name} {bot_info.last_name or ''}".strip()
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка импорта бота: {e}")
        return {"status": "error", "message": f"Ошибка импорта: {str(e)}"}

@app.post("/api/export_bot_zip/{bot_id}/")
def export_bot_zip(bot_id: str):
    """Экспортирует бота в виде ZIP-архива с полным кодом для развертывания"""
    try:
        # Загружаем сценарий и токен
        scenario = load_scenario(bot_id)
        if not scenario.nodes:
            raise HTTPException(status_code=404, detail="Сценарий бота пуст")
        
        token = get_bot_token(bot_id)
        if not token:
            raise HTTPException(status_code=404, detail="Токен бота не найден")
        
        # Создаем временную папку для сборки архива
        with tempfile.TemporaryDirectory() as temp_dir:
            bot_dir = os.path.join(temp_dir, f"bot_{bot_id}")
            os.makedirs(bot_dir)
            
            # Копируем необходимые кодовые файлы
            copy_core_files(bot_dir)
            
            # Создаем конфигурацию бота
            create_bot_config(bot_dir, bot_id, scenario, token)
            
            # Создаем main.py для развертывания
            create_deployment_main(bot_dir, bot_id)
            
            # Создаем requirements.txt
            create_requirements_txt(bot_dir)
            
            # Создаем README с инструкциями
            create_readme(bot_dir, bot_id)
            
            # Создаем ZIP-архив
            zip_path = os.path.join(temp_dir, f"bot_{bot_id}_deploy.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(bot_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_name = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arc_name)
            
            # Копируем архив в доступное место
            final_zip_path = f"bot_{bot_id}_deploy.zip"
            shutil.copy2(zip_path, final_zip_path)
            
            logger.info(f"📦 Экспорт ZIP-архива для бота {bot_id} завершен")
            
            # Возвращаем файл для скачивания
            return FileResponse(
                path=final_zip_path,
                filename=f"bot_{bot_id}_deploy.zip",
                media_type='application/zip'
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка экспорта ZIP-архива бота {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания архива: {str(e)}")

def copy_core_files(bot_dir: str):
    """Копирует необходимые кодовые файлы в папку бота"""
    # Копируем модули blocks
    blocks_src = "blocks"
    blocks_dst = os.path.join(bot_dir, "blocks")
    if os.path.exists(blocks_src):
        shutil.copytree(blocks_src, blocks_dst)
    
    # Копируем модули core
    core_src = "core"
    core_dst = os.path.join(bot_dir, "core")
    if os.path.exists(core_src):
        shutil.copytree(core_src, core_dst)
    
    # Создаем __init__.py файлы
    with open(os.path.join(bot_dir, "__init__.py"), "w") as f:
        f.write("")
    
    with open(os.path.join(blocks_dst, "__init__.py"), "w") as f:
        f.write("")
    
    with open(os.path.join(core_dst, "__init__.py"), "w") as f:
        f.write("")

def create_bot_config(bot_dir: str, bot_id: str, scenario: Scenario, token: str):
    """Создает конфигурационные файлы бота"""
    # Создаем папку bots если её нет
    bots_dir = os.path.join(bot_dir, "bots")
    os.makedirs(bots_dir, exist_ok=True)
    
    # Сохраняем сценарий
    scenario_path = os.path.join(bots_dir, f"bot_{bot_id}.json")
    with open(scenario_path, "w", encoding="utf-8") as f:
        json.dump(scenario.dict(), f, ensure_ascii=False, indent=2)
    
    # Создаем .env файл с токеном
    env_path = os.path.join(bot_dir, ".env")
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"BOT_TOKEN={token}\n")

def create_deployment_main(bot_dir: str, bot_id: str):
    """Создает main.py для развертывания бота на хостинге"""
    main_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Деплоймент бота "{bot_id}" для хостинга
Автоматическое обновление из GitHub репозитория
"""

import os
import sys
import logging
import json
import subprocess
import time
from datetime import datetime, timedelta

# Добавляем текущую директорию в путь поиска модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.scenario_runner import ScenarioRunner
from core.block_registry import block_registry
import telebot
import threading

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Флаг для отслеживания необходимости перезапуска
need_restart = False
last_update_check = datetime.now()


def check_for_updates():
    """Проверяет наличие обновлений в репозитории GitHub"""
    global need_restart, last_update_check
    
    # Проверяем обновления каждые 60 минут
    if datetime.now() - last_update_check < timedelta(minutes=60):
        return False
    
    last_update_check = datetime.now()
    
    try:
        # Проверяем наличие git
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Git не найден, пропускаем проверку обновлений")
            return False
        
        # Проверяем статус репозитория
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Не Git репозиторий, пропускаем проверку обновлений")
            return False
        
        # Получаем последние изменения
        subprocess.run(['git', 'fetch'], check=True)
        
        # Проверяем, есть ли новые коммиты
        local_hash = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True)
        remote_hash = subprocess.run(['git', 'rev-parse', '@{{u}}'], capture_output=True, text=True, check=True)
        
        if local_hash.stdout.strip() != remote_hash.stdout.strip():
            logger.info("Найдены обновления, начинаем обновление...")
            
            # Выполняем обновление
            subprocess.run(['git', 'pull'], check=True)
            
            # Устанавливаем зависимости
            if os.path.exists('requirements.txt'):
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
            
            logger.info("Обновление завершено, требуется перезапуск")
            need_restart = True
            return True
        else:
            logger.info("Обновлений не найдено")
            return False
            
    except subprocess.CalledProcessError as ex:
        logger.error(f"Ошибка при проверке обновлений: {{ex}}")
        return False
    except Exception as ex:
        logger.error(f"Неожиданная ошибка при проверке обновлений: {{ex}}")
        return False


def run_bot():
    """Запускает бота"""
    global need_restart
    
    while True:
        try:
            # Проверяем обновления перед запуском
            if check_for_updates():
                logger.info("Перезапуск бота после обновления...")
                continue
            
            # Загружаем конфигурацию
            # Сначала пробуем загрузить из .env файла
            from dotenv import load_dotenv
            load_dotenv()
            bot_token = os.getenv("BOT_TOKEN")
            
            # Если нет в .env, пробуем получить токен из базы данных
            if not bot_token:
                # Здесь должна быть логика получения токена из базы данных
                # Пока просто возвращаем ошибку
                logger.error("Токен бота не найден")
                return
            
            # Загружаем сценарий
            scenario_path = f"bots/bot_{bot_id}.json"
            if not os.path.exists(scenario_path):
                logger.error("Файл сценария не найден")
                return
            
            with open(scenario_path, "r", encoding="utf-8") as f:
                scenario_data = json.load(f)
            
            # Создаем исполнитель сценария
            scenario_runner = ScenarioRunner(scenario_data)
            if not scenario_runner.nodes_map:
                logger.error("Нет доступных блоков в сценарии!")
                return
            
            # Создаем бота
            bot = telebot.TeleBot(bot_token)
            bot_info = bot.get_me()
            logger.info(f"✅ Бот запущен: @{{bot_info.username}}")
            
            @bot.message_handler(commands=['start', 'help'])
            def handle_start(message):
                try:
                    logger.info(f"👤 /start от {{message.chat.id}} - {{message.from_user.username}}")
                    
                    # Находим стартовый узел
                    start_node = next((node_id for node_id, block in scenario_runner.nodes_map.items()
                                       if hasattr(block, 'type') and block.type == 'start'), None)
                    if start_node:
                        # Запускаем цепочку обработки
                        next_node_id = scenario_runner.process_node(bot, message.chat.id, start_node)
                        while next_node_id:
                            # Проверяем тип следующего узла
                            next_block = scenario_runner.nodes_map.get(next_node_id)
                            if next_block and hasattr(next_block, 'type'):
                                # Если это интерактивные блоки, останавливаем автоматическое выполнение
                                if next_block.type in ['button', 'inline_button', 'input', 'menu']:
                                    scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                    break
                                else:
                                    # Продолжаем для обычных блоков
                                    scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                    next_node_id = scenario_runner.get_next_node_id(next_node_id)
                            else:
                                scenario_runner.process_node(bot, message.chat.id, next_node_id)
                                next_node_id = scenario_runner.get_next_node_id(next_node_id)
                    else:
                        bot.send_message(message.chat.id, "🚀 Бот запущен! Напишите что-нибудь.")
                except Exception as e:
                    logger.error(f"❌ Ошибка в /start: {{e}}")
            
            # Добавляем обработчики для остальных типов блоков (кнопки, inline-кнопки и т.д.)
            # ... (остальные обработчики можно добавить при необходимости)
            
            logger.info("🤖 Бот запущен и ожидает сообщений...")
            
            # Запускаем polling в отдельном потоке для возможности проверки обновлений
            def polling_thread():
                bot.polling(none_stop=True)
            
            poll_thread = threading.Thread(target=polling_thread)
            poll_thread.daemon = True
            poll_thread.start()
            
            # Проверяем обновления каждые 10 минут в основном потоке
            while poll_thread.is_alive():
                time.sleep(600)  # 10 минут
                if check_for_updates():
                    logger.info("Перезапуск бота после обновления...")
                    bot.stop_polling()
                    break
            
        except Exception as e:
            logger.error(f"❌ Ошибка запуска бота: {{e}}")
            
            # Ждем перед повторной попыткой
            time.sleep(10)
            
        # Если мы дошли до этой точки, значит бот остановился
        break


if __name__ == "__main__":
    run_bot()
'''
    
    main_path = os.path.join(bot_dir, "main.py")
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(main_content)

def create_requirements_txt(bot_dir: str):
    """Создает файл зависимостей"""
    requirements_content = '''pyTelegramBotAPI>=4.0.0
requests>=2.25.0
'''
    
    req_path = os.path.join(bot_dir, "requirements.txt")
    with open(req_path, "w", encoding="utf-8") as f:
        f.write(requirements_content)

def create_readme(bot_dir: str, bot_id: str):
    """Создает README с инструкциями по развертыванию"""
    readme_content = f'''# Бот "{bot_id}" для развертывания на хостинге

## Описание
Это полностью готовый к развертыванию бот, экспортированный из конструктора Telegram ботов.

## Структура проекта
- `main.py` - точка входа для запуска бота
- `.env` - файл с токеном бота (рекомендуется)
- `bots/bot_{bot_id}.json` - файл сценария бота
- `blocks/` - папка с блоками бота
- `core/` - папка с ядром системы
- `requirements.txt` - зависимости для установки

## Установка и запуск

1. Установите Python 3.8 или выше
2. Установите зависимости зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл `.env` и добавьте в него токен бота:
   ```
   BOT_TOKEN=ваш_токен_здесь
   ```
4. Запустите бота:
   ```bash
   python main.py
   ```

## Автоматическое обновление из GitHub

Бот поддерживает автоматическое обновление из репозитория GitHub. Для включения этой функции:

1. Создайте репозиторий на GitHub для вашего бота
2. Инициализируйте Git репозиторий в папке бота:
   ```bash
   git init
   git remote add origin <URL_вашего_репозитория>
   git add .
   git commit -m "Initial commit"
   git push -u origin main
   ```

3. Убедитесь, что на сервере установлен Git

4. Бот будет автоматически проверять наличие обновлений каждые 60 минут

5. При наличии обновлений бот:
   - Выполнит `git pull` для получения последних изменений
   - Установит новые зависимости из requirements.txt (если есть)
   - Перезапустится для применения изменений

## Ручная проверка обновлений

Вы также можете вручную проверить обновления, отправив боту команду `/update` (если реализована такая функция) или перезапустив бота.

## Развертывание на хостинге

### Heroku
1. Создайте приложение на Heroku
2. Добавьте buildpack для Python
3. Задеплойте проект
4. Установите переменную окружения для токена (если нужно)

### PythonAnywhere
1. Загрузите все файлы через веб-интерфейс или git
2. Установите зависимости через консоль
3. Запустите main.py как веб-приложение

### Другие хостинги
Бот использует стандартный long polling, поэтому подходит для большинства хостингов.

## Поддержка
Если у вас возникли проблемы с развертыванием, обратитесь к документации конструктору ботов.
'''
    
    readme_path = os.path.join(bot_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)

def get_bot_token(bot_id: str) -> Optional[str]:
    """
    Получает токен бота только из базы данных
    """
    logger.info(f"Получение токена для бота: {bot_id}")
    
    # Проверяем токен в базе данных
    try:
        logger.info("Проверка токена в базе данных")
        
        # Получаем менеджер пользователей
        from core.models import UserManager
        user_manager = UserManager()
        
        # Получаем владельца бота
        owner_id = user_manager.get_bot_owner(bot_id)
        logger.info(f"ID владельца бота {bot_id}: {owner_id}")
        
        if owner_id:
            # Получаем токен владельца для этого бота
            token = user_manager.get_user_token(owner_id, bot_id)
            logger.info(f"Токен из базы данных для бота {bot_id}: {'*' * 10 if token else 'None'}")  # Скрыли отображение токена
            
            if token:
                logger.info(f"Токен для бота {bot_id} найден в базе данных у пользователя {owner_id}")
                return token
            else:
                logger.info(f"Токен не найден в базе данных для бота {bot_id}")
        else:
            logger.info(f"Владелец не найден для бота {bot_id}")
    except Exception as e:
        logger.error(f"Ошибка при чтении токена из базы данных: {e}")
    
    logger.info(f"Токен не найден для бота {bot_id}")
    return None

@app.get("/api/stop_bot/{bot_id}/")
def stop_bot(bot_id: str):
    try:
        if bot_id not in running_bots:
            return {"status": "error", "message": "Бот не запущен."}
        
        logger.info(f"⏹️ Останавливаем бота {bot_id}...")
        
        # Устанавливаем флаг остановки
        bot_stop_flags[bot_id] = True
        
        # Принудительно останавливаем polling если есть экземпляр бота
        bot_instance_key = f"{bot_id}_instance"
        if bot_instance_key in running_bots:
            try:
                bot_instance = running_bots[bot_instance_key]
                logger.info(f".MouseEvent Принудительно останавливаем polling для бота {bot_id}")
                bot_instance.stop_polling()
                del running_bots[bot_instance_key]
                logger.info("✅ Polling остановлен принудительно")
            except Exception as e:
                logger.warning(f"⚠️ Ошибка при остановке polling: {e}")
        
        # Ждем немного чтобы бот корректно остановился
        import time
        time.sleep(3)  # Увеличиваем время ожидания
        
        # Удаляем из running_bots
        if bot_id in running_bots:
            thread = running_bots[bot_id]
            del running_bots[bot_id]
            
            # Проверяем, что поток действительно остановился
            if thread.is_alive():
                logger.warning(f"⚠️ Поток бота {bot_id} все еще активен. Ожидаем еще 2 секунды...")
                time.sleep(2)
                if thread.is_alive():
                    logger.error(f"❌ Поток бота {bot_id} не остановился корректно")
                else:
                    logger.info(f"✅ Поток бота {bot_id} остановлен")
        
        logger.info(f"✅ Бот {bot_id} успешно остановлен")
        return {"status": "success", "message": "Бот успешно остановлен!"}
        
    except Exception as e:
        logger.error(f"❌ Ошибка остановки бота {bot_id}: {e}")
        return {"status": "error", "message": f"Ошибка остановки: {str(e)}"}

@app.post("/api/run_bot/{bot_id}/")
def run_bot_endpoint(bot_id: str, token_data: TokenData):
    """Запускает бота с указанным токеном"""
    try:
        token = token_data.token
        
        # Проверяем валидность токена
        if not validate_telegram_token(token):
            raise HTTPException(status_code=400, detail="Невалидный токен Telegram")
        
        # Проверяем подключение к Telegram
        if not check_token_sync(token):
            raise HTTPException(status_code=400, detail="Не удалось подключиться к Telegram API с этим токеном")
        
        # Останавливаем бота, если он уже запущен
        if bot_id in running_bots:
            logger.info(f"🛑 Бот {bot_id} уже запущен, останавливаем перед перезапуском")
            stop_bot(bot_id)
        
        # Загружаем сценарий
        scenario = load_scenario(bot_id)
        if not scenario.nodes:
            raise HTTPException(status_code=400, detail="Сценарий бота пуст")
        
        # Запускаем бота в отдельном потоке
        bot_thread = threading.Thread(
            target=start_telegram_bot,
            args=(token, scenario.dict(), bot_id),
            name=f"bot_{bot_id}_{bot_restart_counter.get(bot_id, 0)}"
        )
        bot_thread.daemon = True
        bot_thread.start()
        
        # Сохраняем ссылку на поток
        running_bots[bot_id] = bot_thread
        
        # Увеличиваем счетчик перезапусков
        bot_restart_counter[bot_id] = bot_restart_counter.get(bot_id, 0) + 1
        
        logger.info(f"✅ Бот {bot_id} успешно запущен в потоке {bot_thread.name}")
        return {"status": "success", "message": "Бот успешно запущен!"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка запуска бота: {str(e)}")

@app.get("/api/health/")
def health_check():
    return {
        "status": "healthy",
        "network": "ok" if check_telegram_connection() else "error",
        "active_bots": len(running_bots),
        "timestamp": time.time(),
        "message": "Server is running and accepting requests"
    }

# ========== ЭНДПОИНТЫ АВТОРИЗАЦИИ И АУТЕНТИФИКАЦИИ ==========

# Глобальная переменная для менеджера пользователей
user_manager = None

def get_user_manager():
    """Получает экземпляр менеджера пользователей"""
    global user_manager
    if user_manager is None:
        from core.models import UserManager
        user_manager = UserManager()
    return user_manager

@app.options("/api/register/")
async def api_register_options():
    """Обработка OPTIONS запроса для регистрации пользователя"""
    response = JSONResponse({"status": "success"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/api/register/")
async def api_register_user(user_data: RegisterUserRequest):
    """Регистрация нового пользователя"""
    try:
        logger.info(f"Registration attempt with data: username={user_data.username}, email={user_data.email}")
        
        # Проверяем, что все поля заполнены
        if not user_data.username or not user_data.email or not user_data.password:
            logger.warning("Missing required fields in registration request")
            raise HTTPException(status_code=400, detail="Missing required fields")
        
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Регистрируем пользователя
        success = user_manager.register_user(user_data.username, user_data.email, user_data.password)
        
        if success:
            logger.info(f"User {user_data.username} registered successfully")
            response_data = {"status": "success", "message": "User registered successfully"}
            # Добавляем CORS заголовки
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            logger.warning(f"User registration failed for {user_data.username}")
            raise HTTPException(status_code=400, detail="User already exists or registration failed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.options("/api/login/")
async def api_login_options():
    """Обработка OPTIONS запроса для аутентификации пользователя"""
    response = JSONResponse({"status": "success"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/api/login/")
async def api_login_user(user_data: LoginUserRequest):
    """Аутентификация пользователя"""
    try:
        print(f"Login attempt with username: {user_data.username}")
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Аутентифицируем пользователя
        user = user_manager.authenticate_user(user_data.username, user_data.password)
        print(f"Authentication result: {user}")
        
        if user:
            # Возвращаем данные пользователя (без пароля)
            user_dict = user.model_dump()
            user_dict.pop("password_hash", None)
            print(f"User dict: {user_dict}")
            response_data = {"status": "success", "user": user_dict, "message": "Login successful"}
            # Добавляем CORS заголовки
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            print("Invalid credentials")
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# ========== ЭНДПОИНТЫ УПРАВЛЕНИЯ ТОКЕНАМИ ПОЛЬЗОВАТЕЛЕЙ ==========

@app.options("/api/user/save_token/")
async def api_save_user_token_options():
    """Обработка OPTIONS запроса для сохранения токена пользователя"""
    response = JSONResponse({"status": "success"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/api/user/save_token/")
async def api_save_user_token(token_data: SaveTokenRequest):
    """Сохранение токена пользователя"""
    try:
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Сохраняем токен
        success = user_manager.save_user_token(token_data.user_id, token_data.bot_id, token_data.token)
        
        if success:
            response_data = {"message": "Token saved successfully"}
            # Добавляем CORS заголовки
            response = JSONResponse(response_data)
            response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response
        else:
            raise HTTPException(status_code=500, detail="Failed to save token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/user/get_token/{bot_id}/")
async def api_get_user_token(bot_id: str, user_id: str):
    """Получение токена пользователя"""
    try:
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Получаем токен
        token = user_manager.get_user_token(user_id, bot_id)
        
        if token:
            return {"token": token}
        else:
            raise HTTPException(status_code=404, detail="Token not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.options("/api/user/{user_id}/")
async def delete_user_options(user_id: str):
    """Обработка OPTIONS запроса для удаления пользователя"""
    response = JSONResponse({"status": "success"})
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.delete("/api/user/{user_id}/")
def delete_user(user_id: str, deleted_by_user_id: str):
    """Удаление пользователя и всей связанной информации (только для super_admin)"""
    try:
        print(f"API call to delete_user: user_id={user_id}, deleted_by={deleted_by_user_id}")
        
        # Validate input parameters
        if not user_id or not deleted_by_user_id:
            raise HTTPException(status_code=400, detail="User ID and deleted_by_user_id are required")
        
        # Get user manager
        from core.models import UserManager
        user_manager = UserManager()
        
        # Delete user and associated data
        success = user_manager.delete_user_and_associated_data(user_id, deleted_by_user_id)
        
        if success:
            logger.info(f"User {user_id} and all associated data successfully deleted by {deleted_by_user_id}")
            return {"status": "success", "message": "User and all associated data successfully deleted"}
        else:
            raise HTTPException(status_code=400, detail="Failed to delete user or user not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/api/user/delete_token/{bot_id}/")
async def api_delete_user_token(bot_id: str, user_id: str):
    """Удаление токена пользователя"""
    try:
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Удаляем токен
        success = user_manager.delete_user_token(user_id, bot_id)
        
        if success:
            return {"message": "Token deleted successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to delete token")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/bot_status/")
def get_bot_status():
    statuses = {}
    for bot_id, thread in running_bots.items():
        statuses[bot_id] = {
            "is_alive": thread.is_alive(),
            "thread_name": thread.name,
        }
    return statuses

@app.get("/api/bot_running_status/{bot_id}/")
def get_bot_running_status(bot_id: str):
    """Проверяет, запущен ли бот"""
    is_running = bot_id in running_bots and running_bots[bot_id].is_alive()
    return {"is_running": is_running}

@app.get("/api/bot_info/{bot_id}/")
def get_bot_info(bot_id: str):
    scenario = load_scenario(bot_id)
    # Всегда получаем токен из базы данных, а не из переменных окружения
    token = get_bot_token(bot_id)

    node_stats = {}
    for node in scenario.nodes:
        if node.type not in node_stats:
            node_stats[node.type] = 0
        node_stats[node.type] += 1

    return {
        "bot_id": bot_id,
        "has_token": bool(token),
        "nodes_count": len(scenario.nodes),
        "edges_count": len(scenario.edges),
        "node_stats": node_stats,
        "is_running": bot_id in running_bots and running_bots[bot_id].is_alive()
    }

@app.get("/api/get_scenario/{bot_id}/")
def get_scenario(bot_id: str):
    """Загружает сценарий бота из папки bots/"""
    try:
        scenario = load_scenario(bot_id)
        # Используем model_dump для совместимости с Pydantic V2
        scenario_dict = scenario.model_dump()
        
        # Добавляем adminChatId для совместимости с фронтендом
        if 'admin_chat_id' in scenario_dict and scenario_dict['admin_chat_id']:
            scenario_dict['adminChatId'] = scenario_dict['admin_chat_id']
        
        return scenario_dict
    except Exception as e:
        logger.error(f"Ошибка загрузки сценария для бота {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки сценария: {str(e)}")

@app.post("/api/rename_bot/{old_bot_id}/{new_bot_id}/")
def rename_bot(old_bot_id: str, new_bot_id: str):
    """Переименовывает бота"""
    try:
        # Проверяем, что новый ID не пустой
        if not new_bot_id.strip():
            raise HTTPException(status_code=400, detail="Новое имя бота не может быть пустым")
        
        # Проверяем, что бот с новым ID не существует
        new_file_path = bot_file(new_bot_id)
        if os.path.exists(new_file_path):
            raise HTTPException(status_code=400, detail=f"Бот с именем '{new_bot_id}' уже существует")
        
        # Проверяем, что бот с старым ID существует
        old_file_path = bot_file(old_bot_id)
        if not os.path.exists(old_file_path):
            raise HTTPException(status_code=404, detail=f"Бот '{old_bot_id}' не найден")
        
        # Переименовываем файл сценария
        os.rename(old_file_path, new_file_path)
        
        # Обновляем токен в базе данных (если есть)
        try:
            # Получаем менеджер пользователей
            user_manager = get_user_manager()
            
            # Получаем владельца старого бота
            owner_id = user_manager.get_bot_owner(old_bot_id)
            if owner_id:
                # Получаем токен старого бота
                token = user_manager.get_user_token(owner_id, old_bot_id)
                if token:
                    # Удаляем токен старого бота
                    user_manager.delete_user_token(owner_id, old_bot_id)
                    # Сохраняем токен для нового бота
                    user_manager.save_user_token(owner_id, new_bot_id, token)
                
                # Обновляем право собственности
                user_manager.register_bot_ownership(owner_id, new_bot_id)
        except Exception as e:
            logger.error(f"Ошибка обновления токена при переименовании бота: {e}")
        
        # Останавливаем бота, если он запущен
        if old_bot_id in running_bots:
            bot_stop_flags[old_bot_id] = True
            del running_bots[old_bot_id]
        
        logger.info(f"✅ Бот '{old_bot_id}' успешно переименован в '{new_bot_id}'")
        return {
            "status": "success", 
            "message": f"Бот '{old_bot_id}' успешно переименован в '{new_bot_id}'",
            "new_bot_id": new_bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка переименования бота '{old_bot_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка переименования бота: {str(e)}")

@app.get("/api/get_bots/")
def get_bots_endpoint(user_id: Optional[str] = None):
    """Получает список ботов для пользователя или все боты для суперадмина"""
    try:
        # Проверяем, что user_id действителен
        if user_id == "undefined" or not user_id:
            # Return empty list for invalid user_id
            return []
        
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Проверяем, является ли пользователь суперадмином
        is_admin = user_manager.is_super_admin(user_id)
        
        if is_admin:
            # Суперадмин видит все боты
            bots = user_manager.get_all_bots_for_super_admin()
        else:
            # Обычный пользователь видит только свои боты
            bots = user_manager.get_user_bots(user_id)
        
        return bots
    except Exception as e:
        logger.error(f"Ошибка получения списка ботов для пользователя {user_id}: {e}")
        return []

@app.get("/api/get_all_users/")
def get_all_users_endpoint(user_id: Optional[str] = None):
    """Получает список всех пользователей (только для суперадмина)"""
    try:
        # Проверяем, что user_id действителен
        if user_id == "undefined" or not user_id:
            logger.info("Invalid user_id: undefined or empty")
            return []
        
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Проверяем, является ли пользователь суперадмином
        is_admin = user_manager.is_super_admin(user_id)
        logger.info(f"User {user_id} is super admin: {is_admin}")
        
        if is_admin:
            # Суперадмин видит всех пользователей
            users = user_manager.get_all_users()
            logger.info(f"Returning {len(users)} users for super admin {user_id}")
        else:
            # Обычный пользователь не имеет доступа
            users = []
            logger.info(f"User {user_id} is not super admin, returning empty list")
        
        return users
    except Exception as e:
        logger.error(f"Ошибка получения списка всех пользователей для пользователя {user_id}: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

@app.post("/api/create_bot/")
def create_bot(bot_id: str, user_id: str):
    """Создает нового бота с пустым сценарием"""
    try:
        logger.info(f"Создание нового бота: bot_id={bot_id}, user_id={user_id}")
        
        # Проверяем, что bot_id и user_id не пустые
        if not bot_id or not user_id:
            raise HTTPException(status_code=400, detail="Bot ID and User ID are required")
        
        # Проверяем, что бот с таким ID еще не существует
        from core.models import UserManager
        user_manager = UserManager()
        
        # Проверяем, существует ли уже бот с таким ID
        existing_owner = user_manager.get_bot_owner(bot_id)
        if existing_owner:
            raise HTTPException(status_code=400, detail=f"Бот с ID '{bot_id}' уже существует")
        
        # Создаем пустой сценарий
        empty_scenario = Scenario(nodes=[], edges=[])
        
        # Сохраняем пустой сценарий
        save_scenario(bot_id, empty_scenario, user_id)
        
        # Регистрируем право собственности на бота
        user_manager.register_bot_ownership(user_id, bot_id)
        
        logger.info(f"✅ Бот {bot_id} успешно создан для пользователя {user_id}")
        return {
            "status": "success", 
            "message": f"Бот '{bot_id}' успешно создан",
            "bot_id": bot_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка создания бота {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка создания бота: {str(e)}")

@app.post("/api/save_scenario/{bot_id}/")
def save_scenario_endpoint(bot_id: str, scenario: Scenario, user_id: Optional[str] = Query(None)):
    """Сохраняет сценарий бота"""
    try:
        logger.info(f"Сохранение сценария для бота: {bot_id}")
        
        # Сохраняем сценарий
        save_scenario(bot_id, scenario, user_id)
        
        logger.info(f"✅ Сценарий успешно сохранен для бота {bot_id}")
        return {"status": "success", "message": "Сценарий успешно сохранен"}
        
    except ValueError as e:
        logger.error(f"❌ Ошибка сохранения сценария для бота {bot_id}: {e}")
        raise HTTPException(status_code=400, detail=f"Ошибка сохранения сценария: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения сценария для бота {bot_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка сохранения сценария: {str(e)}")

# Инициализация менеджера пользователей
from core.models import UserManager, User, UserToken
from core.db import db

# Генерация ключа для шифрования (в продакшене должен храниться в переменных окружения)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Для разработки генерируем случайный ключ
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    logger.warning("Используется случайный ключ шифрования. В продакшене установите ENCRYPTION_KEY в переменных окружения.")

# Создаем экземпляр шифратора
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_token(token: str) -> str:
    """Шифрует токен"""
    if not token:
        return ""
    try:
        encrypted_token = cipher_suite.encrypt(token.encode())
        return encrypted_token.decode()
    except Exception as e:
        logger.error(f"Ошибка шифрования токена: {e}")
        return ""

def decrypt_token(encrypted_token: str) -> str:
    """Расшифровывает токен"""
    if not encrypted_token:
        return ""
    try:
        decrypted_token = cipher_suite.decrypt(encrypted_token.encode())
        return decrypted_token.decode()
    except Exception as e:
        logger.error(f"Ошибка расшифровки токена: {e}")
        return ""


# ========== ЗАПУСК СЕРВЕРА ==========
if __name__ == "__main__":
    # Создаем папки если их нет
    os.makedirs(BOTS_DIR, exist_ok=True)
    
    # Инициализируем базу данных
    if not db.connect():
        logger.error("Failed to connect to database")
        exit(1)
    
    if not db.create_tables():
        logger.error("Failed to create database tables")
        exit(1)
    
    # Запускаем сервер
    logger.info("🚀 Запуск сервера FastAPI на порту 8002")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,  # Используем порт 8002
        log_level="info"
    )
