import os
import logging
from cryptography.fernet import Fernet
import json

logger = logging.getLogger(__name__)

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

# Функции для аутентификации администратора
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def authenticate_admin(password: str) -> bool:
    """Проверяет пароль администратора"""
    if not ADMIN_PASSWORD:
        logger.warning("Пароль администратора не установлен. В продакшене установите ADMIN_PASSWORD в переменных окружения.")
        return True  # Для разработки разрешаем доступ без пароля
    
    return password == ADMIN_PASSWORD

def hash_password(password: str) -> str:
    """Хеширует пароль (для хранения)"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def encrypt_tokens_file(tokens: dict, file_path: str):
    """Шифрует и сохраняет токены в файл"""
    try:
        # Шифруем каждый токен
        encrypted_tokens = {}
        for bot_id, token in tokens.items():
            encrypted_tokens[bot_id] = encrypt_token(token)
        
        # Сохраняем зашифрованные токены
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(encrypted_tokens, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Токены зашифрованы и сохранены в {file_path}")
    except Exception as e:
        logger.error(f"Ошибка шифрования токенов: {e}")

def decrypt_tokens_file(file_path: str) -> dict:
    """Загружает и расшифровывает токены из файла"""
    try:
        if not os.path.exists(file_path):
            return {}
        
        # Загружаем зашифрованные токены
        with open(file_path, 'r', encoding='utf-8') as f:
            encrypted_tokens = json.load(f)
        
        # Расшифровываем каждый токен
        decrypted_tokens = {}
        for bot_id, encrypted_token in encrypted_tokens.items():
            decrypted_tokens[bot_id] = decrypt_token(encrypted_token)
        
        logger.info(f"Токены расшифрованы из {file_path}")
        return decrypted_tokens
    except Exception as e:
        logger.error(f"Ошибка расшифровки токенов: {e}")
        return {}