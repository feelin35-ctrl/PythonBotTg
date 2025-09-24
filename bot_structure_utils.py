#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Вспомогательные функции для работы с новой структурой папок ботов пользователей
"""

import os
import json
from typing import Optional, Dict, Any
from datetime import datetime

# Путь к директории с ботами
BOTS_DIR = "bots"


def get_bot_directory(user_id: str, bot_id: str) -> str:
    """Возвращает путь к директории бота пользователя"""
    # Убираем префикс "bot_" если он уже есть
    if bot_id.startswith("bot_"):
        clean_bot_id = bot_id
    else:
        clean_bot_id = f"bot_{bot_id}"
    
    bot_dir = os.path.join(BOTS_DIR, f"user_{user_id}", clean_bot_id)
    # Создаем директорию, если она не существует
    os.makedirs(bot_dir, exist_ok=True)
    return bot_dir


def get_bot_scenario_file(user_id: str, bot_id: str) -> str:
    """Возвращает путь к файлу сценария бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    return os.path.join(bot_dir, "scenario.json")


def get_bot_config_file(user_id: str, bot_id: str) -> str:
    """Возвращает путь к конфигурационному файлу бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    return os.path.join(bot_dir, "config.json")


def get_bot_media_directory(user_id: str, bot_id: str) -> str:
    """Возвращает путь к директории медиафайлов бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    media_dir = os.path.join(bot_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    return media_dir


def get_bot_logs_directory(user_id: str, bot_id: str) -> str:
    """Возвращает путь к директории логов бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    logs_dir = os.path.join(bot_dir, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def get_bot_backups_directory(user_id: str, bot_id: str) -> str:
    """Возвращает путь к директории резервных копий бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    backups_dir = os.path.join(bot_dir, "backups")
    os.makedirs(backups_dir, exist_ok=True)
    return backups_dir


def get_bot_temp_directory(user_id: str, bot_id: str) -> str:
    """Возвращает путь к директории временных файлов бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    temp_dir = os.path.join(bot_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    return temp_dir


def create_bot_config(user_id: str, bot_id: str, bot_name: Optional[str] = None) -> bool:
    """Создает конфигурационный файл для бота"""
    try:
        config_file = get_bot_config_file(user_id, bot_id)
        
        # Если файл уже существует, не перезаписываем его
        if os.path.exists(config_file):
            return True
        
        # Создаем конфигурационные данные
        config_data = {
            "bot_id": bot_id,
            "user_id": user_id,
            "bot_name": bot_name or f"Бот {bot_id}",
            "created_at": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "version": "1.0",
            "settings": {
                "active": True,
                "notifications": True,
                "auto_backup": False
            }
        }
        
        # Сохраняем конфигурационный файл
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        print(f"Конфигурационный файл для бота {bot_id} пользователя {user_id} создан")
        return True
    except Exception as e:
        print(f"Ошибка создания конфигурационного файла для бота {bot_id}: {e}")
        return False


def update_bot_config(user_id: str, bot_id: str, updates: Dict[str, Any]) -> bool:
    """Обновляет конфигурационный файл бота"""
    try:
        config_file = get_bot_config_file(user_id, bot_id)
        
        # Если файл не существует, создаем его
        if not os.path.exists(config_file):
            create_bot_config(user_id, bot_id)
        
        # Загружаем существующие данные
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        # Обновляем данные
        for key, value in updates.items():
            if key in config_data:
                config_data[key] = value
            elif key in config_data.get("settings", {}):
                config_data["settings"][key] = value
            else:
                config_data[key] = value
        
        # Обновляем время последнего изменения
        config_data["last_modified"] = datetime.now().isoformat()
        
        # Сохраняем обновленные данные
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        
        print(f"Конфигурационный файл бота {bot_id} пользователя {user_id} обновлен")
        return True
    except Exception as e:
        print(f"Ошибка обновления конфигурационного файла для бота {bot_id}: {e}")
        return False


def save_bot_scenario(user_id: str, bot_id: str, scenario_data: dict) -> bool:
    """Сохраняет сценарий бота в файл"""
    try:
        # Получаем путь к файлу сценария
        scenario_file = get_bot_scenario_file(user_id, bot_id)
        
        # Добавляем метаданные
        if "metadata" not in scenario_data:
            scenario_data["metadata"] = {
                "bot_id": bot_id,
                "user_id": user_id,
                "saved_at": datetime.now().isoformat()
            }
        else:
            scenario_data["metadata"]["saved_at"] = datetime.now().isoformat()
        
        # Сохраняем файл
        with open(scenario_file, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, ensure_ascii=False, indent=2)
        
        print(f"Сценарий бота {bot_id} пользователя {user_id} сохранен в {scenario_file}")
        return True
    except Exception as e:
        print(f"Ошибка сохранения сценария бота {bot_id}: {e}")
        return False


def load_bot_scenario(user_id: str, bot_id: str) -> Optional[dict]:
    """Загружает сценарий бота из файла"""
    try:
        # Получаем путь к файлу сценария
        scenario_file = get_bot_scenario_file(user_id, bot_id)
        
        # Проверяем существование файла
        if not os.path.exists(scenario_file):
            print(f"Файл сценария бота {bot_id} пользователя {user_id} не найден")
            return None
        
        # Загружаем файл
        with open(scenario_file, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        
        print(f"Сценарий бота {bot_id} пользователя {user_id} загружен из {scenario_file}")
        return scenario_data
    except Exception as e:
        print(f"Ошибка загрузки сценария бота {bot_id}: {e}")
        return None


def list_user_bots(user_id: str) -> list:
    """Возвращает список ботов пользователя"""
    try:
        user_dir = os.path.join(BOTS_DIR, f"user_{user_id}")
        
        # Проверяем существование директории пользователя
        if not os.path.exists(user_dir):
            return []
        
        # Получаем список папок ботов
        bot_dirs = []
        for item in os.listdir(user_dir):
            item_path = os.path.join(user_dir, item)
            if os.path.isdir(item_path) and item.startswith("bot_"):
                bot_id = item.replace("bot_", "")
                bot_dirs.append(bot_id)
        
        return bot_dirs
    except Exception as e:
        print(f"Ошибка получения списка ботов пользователя {user_id}: {e}")
        return []


def bot_directory_exists(user_id: str, bot_id: str) -> bool:
    """Проверяет, существует ли директория бота пользователя"""
    bot_dir = get_bot_directory(user_id, bot_id)
    return os.path.exists(bot_dir)


def initialize_bot_structure(user_id: str, bot_id: str, bot_name: Optional[str] = None) -> bool:
    """Инициализирует полную структуру папок для бота пользователя"""
    try:
        # Создаем директорию бота (и все необходимые поддиректории)
        get_bot_directory(user_id, bot_id)
        get_bot_media_directory(user_id, bot_id)
        get_bot_logs_directory(user_id, bot_id)
        get_bot_backups_directory(user_id, bot_id)
        get_bot_temp_directory(user_id, bot_id)
        
        # Создаем конфигурационный файл
        create_bot_config(user_id, bot_id, bot_name)
        
        print(f"Структура папок для бота {bot_id} пользователя {user_id} инициализирована")
        return True
    except Exception as e:
        print(f"Ошибка инициализации структуры папок для бота {bot_id}: {e}")
        return False
