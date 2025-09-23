import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

# Copy the get_bot_token function with debug prints
from typing import Optional
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_user_manager():
    from core.models import UserManager
    return UserManager()

def get_bot_token(bot_id: str) -> Optional[str]:
    """Получение токена бота сначала из переменных окружения, затем из базы данных"""
    print(f"DEBUG: Getting token for bot {bot_id}")
    
    # Сначала проверяем переменные окружения для конкретного бота
    env_token_key = f"BOT_TOKEN_{bot_id.upper()}"
    env_token = os.getenv(env_token_key)
    if env_token:
        print(f"DEBUG: Token for bot {bot_id} found in environment variables")
        return env_token
    
    # Затем проверяем общий токен из переменных окружения
    env_token = os.getenv("BOT_TOKEN")
    if env_token:
        print(f"DEBUG: Using general BOT_TOKEN environment variable for bot {bot_id}")
        return env_token
    
    # Проверяем токен в базе данных
    try:
        print(f"DEBUG: Checking database for token")
        # Получаем менеджер пользователей
        user_manager = get_user_manager()
        
        # Получаем владельца бота
        owner_id = user_manager.get_bot_owner(bot_id)
        print(f"DEBUG: Owner ID for bot {bot_id}: {owner_id}")
        if owner_id:
            # Получаем токен владельца для этого бота
            token = user_manager.get_user_token(owner_id, bot_id)
            print(f"DEBUG: Token from database for bot {bot_id}: {token}")
            if token:
                print(f"DEBUG: Token for bot {bot_id} found in database for user {owner_id}")
                return token
            else:
                print(f"DEBUG: No token found in database for bot {bot_id}")
        else:
            print(f"DEBUG: No owner found for bot {bot_id}")
    except Exception as e:
        print(f"DEBUG: Error reading token from database: {e}")
    
    print(f"DEBUG: No token found for bot {bot_id}")
    return None

# Test the function
bot_id = "mainBot"
token = get_bot_token(bot_id)
print(f"Final result: {token}")