from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import os, json, time
from fastapi.middleware.cors import CORSMiddleware
import telebot
import threading
import uvicorn
import logging
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Импорты архитектуры блоков
from core.block_registry import block_registry
from core.scenario_runner import ScenarioRunner

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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


# ========== НАСТРОЙКИ ==========
BOTS_DIR = "bots"
os.makedirs(BOTS_DIR, exist_ok=True)
TOKENS_FILE = "bot_tokens.json"

# Глобальные словари для управления ботами
running_bots = {}
bot_stop_flags = {}


def load_tokens():
    if os.path.exists(TOKENS_FILE):
        try:
            with open(TOKENS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_tokens(tokens):
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

            @bot.message_handler(commands=['start', 'help'])
            def handle_start(message):
                try:
                    logger.info(f"👤 /start от {message.chat.id} - {message.from_user.username}")
                    # Находим стартовый узел
                    start_node = next((node_id for node_id, block in scenario_runner.nodes_map.items()
                                       if hasattr(block, 'type') and block.type == 'start'), None)
                    if start_node:
                        # Запускаем цепочку обработки
                        next_node_id = scenario_runner.process_node(bot, message.chat.id, start_node)
                        while next_node_id:
                            next_node_id = scenario_runner.process_node(bot, message.chat.id, next_node_id)
                    else:
                        bot.send_message(message.chat.id, "🚀 Бот запущен! Напишите что-нибудь.")
                except Exception as e:
                    logger.error(f"❌ Ошибка в /start: {e}")

            # Обработчик callback-запросов (inline-кнопки)
            @bot.callback_query_handler(func=lambda call: True)
            def handle_callback_query(call):
                try:
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
                    logger.info(f"💬 Сообщение от {message.chat.id}: {message.text}")

                    # Проверяем, является ли сообщение нажатием на кнопку
                    for node_id, block in scenario_runner.nodes_map.items():
                        if hasattr(block, 'type') and block.type == 'button':
                            buttons = block.node_data.get('data', {}).get('buttons', [])
                            for index, button in enumerate(buttons):
                                if button.get('label') == message.text:
                                    logger.info(f"🔘 Нажата кнопка: {message.text}")
                                    result = scenario_runner.handle_button_press(bot, message.chat.id, node_id, index)
                                    if result:
                                        return

                    # Если не кнопка, отправляем стандартный ответ
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
                    bot.polling(
                        none_stop=True,
                        interval=2,
                        timeout=20,
                        long_polling_timeout=20
                    )
                except Exception as e:
                    if bot_stop_flags.get(bot_id, True):
                        break
                    logger.error(f"🔥 Ошибка polling: {e}")
                    logger.info("🔄 Перезапуск polling через 10 секунд...")
                    time.sleep(10)

            logger.info(f"⏹️ Бот {bot_id} остановлен")
            break

        except telebot.apihelper.ApiException as e:
            if "Unauthorized" in str(e):
                logger.error("🚫 Неверный токен! Остановка бота.")
                break
            logger.error(f"❌ Ошибка Telegram API: {e}")
            time.sleep(retry_delay)
        except Exception as e:
            logger.error(f"🔥 Критическая ошибка бота: {e}")
            time.sleep(retry_delay)


# ========== API ЭНДПОИНТЫ ==========
@app.get("/")
def read_root():
    return {"message": "Telegram Bot Constructor API"}


@app.get("/get_bots/")
def get_bots():
    bots = []
    for filename in os.listdir(BOTS_DIR):
        if filename.startswith("bot_") and filename.endswith(".json"):
            bot_id = filename.replace("bot_", "").replace(".json", "")
            bots.append(bot_id)
    return {"bots": bots}


@app.post("/create_bot/")
def create_bot(bot_id: str):
    path = bot_file(bot_id)
    if os.path.exists(path):
        return {"status": "error", "message": "Бот уже существует"}
    save_scenario(bot_id, Scenario(nodes=[], edges=[]))
    return {"status": "success"}


@app.get("/get_scenario/{bot_id}/")
def get_scenario(bot_id: str):
    scenario = load_scenario(bot_id)
    return scenario


@app.post("/save_scenario/{bot_id}/")
def save_bot_scenario(bot_id: str, scenario: Scenario):
    logger.info(f"💾 Сохраняем сценарий для бота {bot_id}")
    save_scenario(bot_id, scenario)
    return {"status": "success"}


@app.delete("/delete_bot/{bot_id}/")
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


@app.post("/save_token/{bot_id}/")
def save_bot_token(bot_id: str, token_data: Dict[str, str]):
    tokens = load_tokens()
    tokens[bot_id] = token_data.get("token", "")
    save_tokens(tokens)
    logger.info(f"Токен сохранен для бота {bot_id}")
    return {"status": "success"}


@app.get("/get_token/{bot_id}/")
def get_bot_token(bot_id: str):
    tokens = load_tokens()
    token = tokens.get(bot_id, "")
    return {"token": token}


@app.delete("/delete_token/{bot_id}/")
def delete_bot_token(bot_id: str):
    tokens = load_tokens()
    if bot_id in tokens:
        del tokens[bot_id]
        save_tokens(tokens)
        return {"status": "success"}
    return {"status": "error", "message": "Токен не найден"}


@app.get("/check_token/{token}/")
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


@app.get("/check_bot/{token}/")
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


@app.get("/available_blocks/")
def get_available_blocks():
    """Возвращает список доступных типов блоков"""
    try:
        blocks = block_registry.get_available_blocks()
        return {"blocks": blocks}
    except Exception as e:
        logger.error(f"Ошибка получения списка блоков: {e}")
        return {"blocks": []}


@app.post("/run_bot/{bot_id}/")
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

    bot_token = token.get("token", "").strip()
    if not bot_token:
        return {"status": "error", "message": "Токен не предоставлен."}

    if not validate_telegram_token(bot_token):
        return {"status": "error", "message": "Неверный формат токена."}

    # Проверяем токен
    try:
        test_bot = telebot.TeleBot(bot_token)
        bot_info = test_bot.get_me()
        logger.info(f"✅ Токен верный. Бот: @{bot_info.username}")
    except telebot.apihelper.ApiException as e:
        if "Unauthorized" in str(e):
            return {"status": "error", "message": "Неверный токен"}
        else:
            return {"status": "error", "message": f"Ошибка Telegram API: {str(e)}"}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка проверки токена: {str(e)}"}

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


@app.post("/restart_bot/{bot_id}/")
def restart_bot(bot_id: str):
    """Останавливает и перезапускает бота"""
    try:
        # Устанавливаем флаг остановки
        bot_stop_flags[bot_id] = True

        # Ждем немного чтобы бот корректно остановился
        time.sleep(2)

        # Удаляем из running_bots
        if bot_id in running_bots:
            del running_bots[bot_id]

        logger.info(f"⏹️ Бот {bot_id} остановлен")

        # Загружаем сценарий и токен
        scenario_data = load_scenario(bot_id)
        tokens = load_tokens()
        bot_token = tokens.get(bot_id, "")

        if not bot_token:
            return {"status": "error", "message": "Токен не найден"}

        if not scenario_data.nodes:
            return {"status": "error", "message": "Сценарий пуст"}

        # Запускаем бота заново
        thread = threading.Thread(
            target=start_telegram_bot,
            args=(bot_token, scenario_data.dict(), bot_id),
            name=f"Bot_{bot_id}"
        )
        thread.daemon = True
        thread.start()
        running_bots[bot_id] = thread

        return {"status": "success", "message": "Бот успешно перезапущен!"}

    except Exception as e:
        return {"status": "error", "message": f"Ошибка перезапуска: {str(e)}"}


@app.get("/stop_bot/{bot_id}/")
def stop_bot(bot_id: str):
    if bot_id in running_bots:
        bot_stop_flags[bot_id] = True
        del running_bots[bot_id]
        return {"status": "success", "message": "Попытка остановки бота."}
    return {"status": "error", "message": "Бот не запущен."}


@app.get("/health/")
def health_check():
    return {
        "status": "healthy",
        "network": "ok" if check_telegram_connection() else "error",
        "active_bots": len(running_bots),
        "timestamp": time.time()
    }


@app.get("/bot_status/")
def get_bot_status():
    statuses = {}
    for bot_id, thread in running_bots.items():
        statuses[bot_id] = {
            "is_alive": thread.is_alive(),
            "thread_name": thread.name,
        }
    return statuses

@app.get("/bot_running_status/{bot_id}/")
def get_bot_running_status(bot_id: str):
    """Проверяет, запущен ли бот"""
    is_running = bot_id in running_bots and running_bots[bot_id].is_alive()
    return {"is_running": is_running}

@app.get("/bot_info/{bot_id}/")
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


# ========== ЗАПУСК СЕРВЕРА ==========
if __name__ == "__main__":
    # Создаем папки если их нет
    os.makedirs(BOTS_DIR, exist_ok=True)

    # Запускаем сервер
    logger.info("🚀 Запуск сервера FastAPI на порту 8001")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
        timeout_keep_alive=30
    )