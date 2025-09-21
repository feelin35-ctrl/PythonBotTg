from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import os, json, time, zipfile, tempfile, shutil
from fastapi.middleware.cors import CORSMiddleware
import telebot
import threading
import uvicorn
import logging
import requests
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
    "http://45.150.9.70"  # Добавляем адрес без порта для продакшена
]

# Добавляем дополнительные origins из переменной окружения
additional_origins = os.getenv("ALLOWED_ORIGINS", "")
if additional_origins:
    allowed_origins.extend(additional_origins.split(","))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== МОДЕЛИ ==========
class ButtonData(BaseModel):
    label: str


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


class BotImportData(BaseModel):
    bot_id: str
    scenario: Scenario
    token: str


# ========== НАСТРОЙКИ ==========
BOTS_DIR = "bots"
os.makedirs(BOTS_DIR, exist_ok=True)
TOKENS_FILE = "bot_tokens.json"

# Глобальные словари для управления ботами
running_bots = {}
bot_stop_flags = {}
bot_restart_counter = {}  # Счетчик перезапусков для уникальных имен потоков
chat_history = {}  # Храним историю переходов для каждого чата


def load_tokens():
    # Проверяем, есть ли переменная окружения BOT_TOKEN
    env_token = os.getenv("BOT_TOKEN")
    if env_token:
        # Если есть переменная окружения, используем её
        logger.info("Используется токен из переменной окружения BOT_TOKEN")
        return {"env_bot": env_token}
    
    # Если нет переменной окружения, используем файл как раньше
    if os.path.exists(TOKENS_FILE):
        try:
            logger.info(f"Читаем токены из файла {TOKENS_FILE}")
            with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
                tokens = json.load(f)
                logger.info(f"Загружены токены: {list(tokens.keys())}")
                return tokens
        except Exception as e:
            logger.error(f"Ошибка загрузки токенов из файла: {e}")
            return {}
    else:
        logger.info(f"Файл токенов {TOKENS_FILE} не найден")
    return {}


def save_tokens(tokens):
    # Если используется переменная окружения, не сохраняем в файл
    if os.getenv("BOT_TOKEN"):
        return
    
    with open(TOKENS_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f, ensure_ascii=False, indent=2)


def bot_file(bot_id: str) -> str:
    return os.path.join(BOTS_DIR, f"bot_{bot_id}.json")


def load_scenario(bot_id: str) -> Scenario:
    file_path = bot_file(bot_id)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return Scenario(**data)
        except Exception as e:
            logger.error(f"Ошибка загрузки сценария {bot_id}: {e}")
            return Scenario(nodes=[], edges=[])
    return Scenario(nodes=[], edges=[])


def save_scenario(bot_id: str, scenario: Scenario):
    try:
        with open(bot_file(bot_id), "w", encoding="utf-8") as f:
            json.dump(scenario.dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Сценарий сохранен для бота {bot_id}")
    except Exception as e:
        logger.error(f"Ошибка сохранения сценария {bot_id}: {e}")


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
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
    logger.info(f"🔄 Запуск бота {bot_id} с токеном: {token[:10]}...")

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

            # Создаем основного бота
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
                        'chat_id': message.chat.id,
                        'user_id': message.from_user.id,
                        'username': message.from_user.username
                    }

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


# ========== API ЭНДПОИНТЫ ==========
@app.get("/")
def read_root():
    return {"message": "Telegram Bot Constructor API"}


@app.post("/api/import_bot/")
def import_bot(import_data: BotImportData):
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
        
        # Сохраняем токен
        logger.info(f"🔑 Импортируем токен для бота {bot_id}")
        tokens = load_tokens()
        tokens[bot_id] = token
        save_tokens(tokens)
        
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
        
        tokens = load_tokens()
        token = tokens.get(bot_id, "")
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
    
    # Создаем файл токенов или .env файл
    tokens_path = os.path.join(bot_dir, "bot_tokens.json")
    env_path = os.path.join(bot_dir, ".env")
    
    # Создаем .env файл с токеном
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(f"BOT_TOKEN={token}\n")
    
    # Создаем пустой файл токенов для совместимости
    tokens_data = {bot_id: ""}  # Пустой токен, так как теперь используется .env
    with open(tokens_path, "w", encoding="utf-8") as f:
        json.dump(tokens_data, f, ensure_ascii=False, indent=2)


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
            
            # Если нет в .env, пробуем загрузить из файла токенов
            if not bot_token:
                tokens_path = "bot_tokens.json"
                if not os.path.exists(tokens_path):
                    logger.error("Файл токенов не найден")
                    return
                
                with open(tokens_path, "r", encoding="utf-8") as f:
                    tokens = json.load(f)
                
                bot_token = tokens.get("{bot_id}")
                if not bot_token:
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
- `bot_tokens.json` - файл с токеном бота (альтернативный способ)
- `bots/bot_{bot_id}.json` - файл сценария бота
- `blocks/` - папка с блоками бота
- `core/` - папка с ядром системы
- `requirements.txt` - зависимости для установки

## Установка и запуск

1. Установите Python 3.8 или выше
2. Установите зависимости:
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
Если у вас возникли проблемы с развертыванием, обратитесь к документации конструкторуктора ботов.
'''
    
    readme_path = os.path.join(bot_dir, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)


@app.get("/api/get_bots/")
def get_bots():
    bots = []
    # Явно указываем кодировку для чтения файлов
    filenames = os.listdir(BOTS_DIR)
    logger.info(f"Найдено файлов в директории {BOTS_DIR}: {filenames}")
    for filename in filenames:
        if filename.startswith("bot_") and filename.endswith(".json"):
            # Обрабатываем кодировку имен файлов с кириллицей
            try:
                # Пытаемся декодировать имя файла
                bot_id = filename.replace("bot_", "").replace(".json", "")
                logger.info(f"Обрабатываем файл бота: {filename}, bot_id: {bot_id}")
                # Проверяем, есть ли проблема с кодировкой
                if 'Ð' in bot_id or 'Ñ' in bot_id:
                    # Пробуем перекодировать из latin-1 в utf-8
                    bot_id_bytes = bot_id.encode('latin-1')
                    bot_id = bot_id_bytes.decode('utf-8')
                bots.append(bot_id)
            except Exception as e:
                logger.error(f"Ошибка обработки файла {filename}: {e}")
                # Если не удалось перекодировать, используем оригинальное имя
                bot_id = filename.replace("bot_", "").replace(".json", "")
                bots.append(bot_id)
    logger.info(f"Возвращаем список ботов: {bots}")
    # Явно указываем кодировку в заголовках ответа
    import json
    response_data = {"bots": bots}
    response_json = json.dumps(response_data, ensure_ascii=False).encode('utf-8')
    from fastapi.responses import Response
    return Response(content=response_json, media_type="application/json; charset=utf-8")


@app.post("/api/create_bot/")
def create_bot(bot_id: str):
    path = bot_file(bot_id)
    if os.path.exists(path):
        return {"status": "error", "message": "Бот уже существует"}
    save_scenario(bot_id, Scenario(nodes=[], edges=[]))
    return {"status": "success"}


@app.get("/api/get_scenario/{bot_id}/")
def get_scenario(bot_id: str):
    scenario = load_scenario(bot_id)
    # Явно указываем кодировку UTF-8 в заголовках ответа
    return scenario


@app.post("/api/save_scenario/{bot_id}/")
def save_bot_scenario(bot_id: str, scenario: Scenario):
    logger.info(f"💾 Сохраняем сценарий для бота {bot_id}")
    save_scenario(bot_id, scenario)
    return {"status": "success"}


@app.delete("/api/delete_bot/{bot_id}/")
def delete_bot(bot_id: str):
    file_path = bot_file(bot_id)
    if os.path.exists(file_path):
        os.remove(file_path)
        tokens = load_tokens()
        if bot_id in tokens:
            del tokens[bot_id]
            save_tokens(tokens)

        # Останавливаем бота если он запущен
        if bot_id in running_bots:
            bot_stop_flags[bot_id] = True
            del running_bots[bot_id]

        return {"status": "success", "message": f"Бот {bot_id} успешно удален."}
    raise HTTPException(status_code=404, detail=f"Бот {bot_id} не найден.")


@app.post("/api/save_token/{bot_id}/")
def save_bot_token(bot_id: str, token_data: Dict[str, str]):
    tokens = load_tokens()
    tokens[bot_id] = token_data.get("token", "")
    save_tokens(tokens)
    logger.info(f"Токен сохранен для бота {bot_id}")
    return {"status": "success"}


@app.get("/api/get_token/{bot_id}/")
def get_bot_token(bot_id: str):
    tokens = load_tokens()
    # Проверяем, используется ли переменная окружения BOT_TOKEN
    env_token = os.getenv("BOT_TOKEN")
    if env_token:
        # Если используется переменная окружения, возвращаем её для всех ботов
        token = env_token
    else:
        # Если нет переменной окружения, ищем токен по bot_id
        token = tokens.get(bot_id, "")
    return {"token": token}


# Добавляем новые эндпоинты для управления именем бота
@app.post("/api/set_bot_name/{bot_id}/")
def set_bot_name(bot_id: str, name_data: Dict[str, str]):
    """Устанавливает имя бота в Telegram"""
    try:
        tokens = load_tokens()
        # Проверяем, используется ли переменная окружения BOT_TOKEN
        env_token = os.getenv("BOT_TOKEN")
        if env_token:
            # Если используется переменная окружения, используем её для всех ботов
            bot_token = env_token
        else:
            # Если нет переменной окружения, ищем токен по bot_id
            bot_token = tokens.get(bot_id, "")
        
        if not bot_token:
            raise HTTPException(status_code=404, detail="Токен бота не найден")
        
        bot_name = name_data.get("name", "").strip()
        if not bot_name:
            raise HTTPException(status_code=400, detail="Имя бота не может быть пустым")
        
        # Используем pyTelegramBotAPI для установки имени бота
        bot = telebot.TeleBot(bot_token)
        result = bot.set_my_name(bot_name)
        
        if result:
            logger.info(f"✅ Имя бота '{bot_id}' успешно изменено на '{bot_name}'")
            return {
                "status": "success", 
                "message": f"Имя бота успешно изменено на '{bot_name}'",
                "name": bot_name
            }
        else:
            raise HTTPException(status_code=500, detail="Не удалось изменить имя бота")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка установки имени бота '{bot_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка установки имени бота: {str(e)}")


@app.get("/api/get_bot_name/{bot_id}/")
def get_bot_name(bot_id: str):
    """Получает текущее имя бота из Telegram"""
    try:
        tokens = load_tokens()
        logger.info(f"Все доступные токены: {list(tokens.keys())}")
        logger.info(f"Запрошенный bot_id: {bot_id}")
        
        # Проверяем, используется ли переменная окружения BOT_TOKEN
        env_token = os.getenv("BOT_TOKEN")
        if env_token:
            # Если используется переменная окружения, используем её для всех ботов
            bot_token = env_token
            logger.info("Используется токен из переменной окружения BOT_TOKEN для всех ботов")
        else:
            # Если нет переменной окружения, ищем токен по bot_id
            bot_token = tokens.get(bot_id, "")
        
        logger.info(f"Найденный токен: {bot_token}")
        
        if not bot_token:
            logger.error(f"Токен бота '{bot_id}' не найден")
            raise HTTPException(status_code=404, detail="Токен бота не найден")
        
        # Используем pyTelegramBotAPI для получения имени бота
        bot = telebot.TeleBot(bot_token)
        bot_info = bot.get_me()
        current_name = bot_info.first_name
        
        return {
            "status": "success",
            "name": current_name
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения имени бота '{bot_id}': {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения имени бота: {str(e)}")


@app.delete("/api/delete_token/{bot_id}/")
def delete_bot_token(bot_id: str):
    tokens = load_tokens()
    if bot_id in tokens:
        del tokens[bot_id]
        save_tokens(tokens)
        return {"status": "success"}
    return {"status": "error", "message": "Токен не найден"}


@app.get("/api/check_token/{token}/")
def check_token(token: str):
    try:
        if not validate_telegram_token(token):
            return {"valid": False, "message": "Неверный формат токена"}

        test_bot = telebot.TeleBot(token)
        bot_info = test_bot.get_me()

        return {
            "valid": True,
            "message": "Токен действителен",
            "bot_username": bot_info.username,
            "bot_name": f"{bot_info.first_name} {bot_info.last_name or ''}".strip()
        }

    except Exception as e:
        return {"valid": False, "message": f"Ошибка: {str(e)}"}


@app.get("/api/check_bot/{token}/")
def check_bot(token: str):
    """Проверяет, доступен ли бот с данным токеном"""
    try:
        bot = telebot.TeleBot(token)
        bot_info = bot.get_me()
        return {
            "status": "success",
            "username": f"@{bot_info.username}",
            "name": f"{bot_info.first_name} {bot_info.last_name or ''}".strip(),
            "id": bot_info.id
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/api/available_blocks/")
def get_available_blocks():
    """Возвращает список доступных типов блоков"""
    try:
        blocks = block_registry.get_available_blocks()
        return {"blocks": blocks}
    except Exception as e:
        logger.error(f"Ошибка получения списка блоков: {e}")
        return {"blocks": []}


@app.post("/api/run_bot/{bot_id}/")
def run_bot(bot_id: str, token: Dict[str, str]):
    if bot_id in running_bots and running_bots[bot_id].is_alive():
        return {"status": "error", "message": "Бот уже запущен."}

    # Проверяем сеть
    try:
        response = requests.get('https://api.telegram.org', timeout=10)
        if response.status_code != 200:
            return {"status": "error", "message": "Нет подключения к Telegram API"}
    except:
        return {"status": "error", "message": "Нет интернет-соединения"}

    scenario_data = load_scenario(bot_id)
    if not scenario_data.nodes:
        return {"status": "error", "message": "Сценарий пуст."}

    # Проверяем, используется ли переменная окружения BOT_TOKEN
    env_token = os.getenv("BOT_TOKEN")
    if env_token:
        # Если используется переменная окружения, используем её для всех ботов
        bot_token = env_token
        logger.info("Используется токен из переменной окружения BOT_TOKEN для запуска бота")
    else:
        # Если нет переменной окружения, получаем токен из параметров или из файла
        bot_token = token.get("token", "").strip()
        if not bot_token:
            # Если токен не передан в параметрах, пытаемся получить его из файла
            tokens = load_tokens()
            bot_token = tokens.get(bot_id, "").strip()

    if not bot_token:
        return {"status": "error", "message": "Токен не предоставлен."}

    if not validate_telegram_token(bot_token):
        return {"status": "error", "message": "Неверный формат токена."}

    # Проверяем токен
    try:
        test_bot = telebot.TeleBot(bot_token)
        bot_info = test_bot.get_me()
        logger.info(f"✅ Токен верный. Бот: @{bot_info.username}")
    except Exception as e:
        if "Unauthorized" in str(e):
            return {"status": "error", "message": "Неверный токен"}
        else:
            return {"status": "error", "message": f"Ошибка Telegram API: {str(e)}"}

    try:
        thread = threading.Thread(
            target=start_telegram_bot,
            args=(bot_token, scenario_data.dict(), bot_id),
            name=f"Bot_{bot_id}"
        )
        thread.daemon = True
        thread.start()
        running_bots[bot_id] = thread

        return {"status": "success", "message": "Бот успешно запущен!"}

    except Exception as e:
        return {"status": "error", "message": f"Ошибка запуска: {str(e)}"}


@app.post("/api/restart_bot/{bot_id}/")
def restart_bot(bot_id: str):
    """Останавливает и перезапускает бота"""
    try:
        logger.info(f"🔄 Начинаем перезапуск бота {bot_id}...")
        
        # 1. Сначала устанавливаем флаг остановки
        bot_stop_flags[bot_id] = True
        logger.info(f"⏹️ Установлен флаг остановки для бота {bot_id}")

        # 2. Если бот запущен, ждем его остановки
        if bot_id in running_bots:
            thread = running_bots[bot_id]
            logger.info(f"⏳ Ожидаем остановки старого экземпляра бота {bot_id}...")
            
            # Принудительно останавливаем polling если есть экземпляр бота
            bot_instance_key = f"{bot_id}_instance"
            if bot_instance_key in running_bots:
                try:
                    old_bot_instance = running_bots[bot_instance_key]
                    logger.info(f".MouseEvent Принудительно останавливаем polling для бота {bot_id}")
                    old_bot_instance.stop_polling()
                    del running_bots[bot_instance_key]
                    logger.info("✅ Polling остановлен принудительно")
                except Exception as e:
                    logger.warning(f"⚠️ Ошибка при остановке polling: {e}")
            
            # Ждем до 15 секунд для корректной остановки
            max_wait_time = 15
            wait_step = 0.5
            waited = 0
            
            while thread.is_alive() and waited < max_wait_time:
                time.sleep(wait_step)
                waited += wait_step
                if waited % 3 == 0:  # Логируем каждые 3 секунды
                    logger.info(f"⏳ Ожидание остановки... ({waited}s/{max_wait_time}s)")
            
            if thread.is_alive():
                logger.warning(f"⚠️ Бот {bot_id} не остановился за {max_wait_time}s, принудительно продолжаем")
            else:
                logger.info(f"✅ Старый экземпляр бота {bot_id} остановлен")
            
            # Удаляем из running_bots
            del running_bots[bot_id]
        else:
            logger.info(f"ℹ️ Бот {bot_id} не был запущен, запускаем новый экземпляр")

        # 3. Дополнительная пауза для полной очистки соединений Telegram
        logger.info("⏳ Дополнительная пауза перед запуском нового экземпляра...")
        time.sleep(5)  # Увеличиваем паузу до 5 секунд

        # 4. Загружаем сценарий и токен
        scenario_data = load_scenario(bot_id)
        tokens = load_tokens()
        bot_token = tokens.get(bot_id, "")

        if not bot_token:
            return {"status": "error", "message": "Токен не найден"}

        if not scenario_data.nodes:
            return {"status": "error", "message": "Сценарий пуст"}

        # 5. Запускаем нового бота
        logger.info(f"🚀 Запускаем новый экземпляр бота {bot_id}...")
        
        # Увеличиваем счетчик перезапусков
        bot_restart_counter[bot_id] = bot_restart_counter.get(bot_id, 0) + 1
        restart_num = bot_restart_counter[bot_id]
        
        thread = threading.Thread(
            target=start_telegram_bot,
            args=(bot_token, scenario_data.dict(), bot_id),
            name=f"Bot_{bot_id}_restart_{restart_num}"
        )
        thread.daemon = True
        thread.start()
        running_bots[bot_id] = thread

        logger.info(f"✅ Бот {bot_id} успешно перезапущен! (перезапуск #{restart_num})")
        return {"status": "success", "message": f"Бот успешно перезапущен! (перезапуск #{restart_num})"}

    except Exception as e:
        logger.error(f"❌ Ошибка перезапуска бота {bot_id}: {e}")
        return {"status": "error", "message": f"Ошибка перезапуска: {str(e)}"}


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


@app.get("/api/health/")
def health_check():
    return {
        "status": "healthy",
        "network": "ok" if check_telegram_connection() else "error",
        "active_bots": len(running_bots),
        "timestamp": time.time()
    }


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
    tokens = load_tokens()
    token = tokens.get(bot_id, "")

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
        
        # Обновляем токен (если есть)
        tokens = load_tokens()
        if old_bot_id in tokens:
            token = tokens[old_bot_id]
            del tokens[old_bot_id]
            tokens[new_bot_id] = token
            save_tokens(tokens)
        
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


# ========== ЗАПУСК СЕРВЕРА ==========
if __name__ == "__main__":
    # Создаем папки если их нет
    os.makedirs(BOTS_DIR, exist_ok=True)

    # Запускаем сервер
    logger.info("🚀 Запуск сервера FastAPI на порту 8001")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,  # Исправлено: используем порт 8001 согласно настройкам проекта
        log_level="info",
        timeout_keep_alive=30
    )