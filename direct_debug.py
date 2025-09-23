import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

# Test the get_bot_token function directly
import json
import logging
from typing import Optional
from core.models import UserManager
from core.db import db

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a global user manager instance
user_manager = None

def get_user_manager():
    """Получает экземпляр менеджера пользователей"""
    global user_manager
    if user_manager is None:
        user_manager = UserManager()
    return user_manager

def get_bot_token(bot_id: str) -> Optional[str]:
    """Получение токена бота сначала из переменных окружения, затем из базы данных"""
    print(f"DEBUG: Looking for token for bot {bot_id}")
    
    # Сначала проверяем переменные окружения для конкретного бота
    env_token_key = f"BOT_TOKEN_{bot_id.upper()}"
    env_token = os.getenv(env_token_key)
    if env_token:
        logger.info(f"Token for bot {bot_id} found in environment variables")
        return env_token
    
    # Затем проверяем общий токен из переменных окружения
    env_token = os.getenv("BOT_TOKEN")
    if env_token:
        logger.info(f"Using general BOT_TOKEN environment variable for bot {bot_id}")
        return env_token
    
    # Проверяем токен в базе данных
    try:
        print("DEBUG: Checking database for token")
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Получаем владельца бота
        owner_id = user_manager.get_bot_owner(bot_id)
        print(f"DEBUG: Owner ID: {owner_id}")
        if owner_id:
            # Получаем токен владельца для этого бота
            token = user_manager.get_user_token(owner_id, bot_id)
            print(f"DEBUG: Token from database: {token}")
            if token:
                logger.info(f"Token for bot {bot_id} found in database for user {owner_id}")
                return token
    except Exception as e:
        logger.error(f"Error reading token from database: {e}")
        import traceback
        traceback.print_exc()
    
    print("DEBUG: No token found")
    return None

token = get_bot_token('testBot123')
print(f'Final Token: {token}')