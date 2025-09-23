import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

# Создаем экземпляр UserManager
user_manager = UserManager()

# Пытаемся аутентифицировать пользователя
user = user_manager.authenticate_user("Feelin", "newpassword")

if user:
    print("Аутентификация успешна!")
    print(f"User ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Is admin: {user.is_admin}")
else:
    print("Аутентификация не удалась!")