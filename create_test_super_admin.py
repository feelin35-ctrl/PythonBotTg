import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

def create_test_super_admin():
    """Создает тестового супер администратора"""
    try:
        user_manager = UserManager()
        
        # Регистрируем тестового супер администратора
        username = "superadmin"
        email = "admin@example.com"
        password = "superpassword123"
        
        success = user_manager.register_user(username, email, password, role="super_admin")
        
        if success:
            print(f"✅ Тестовый супер администратор '{username}' успешно создан")
            print(f"Email: {email}")
            print(f"Пароль: {password}")
            print("Теперь этот пользователь может видеть всех ботов в системе")
        else:
            print(f"❌ Не удалось создать тестового супер администратора '{username}'")
            print("Возможно, пользователь с таким именем или email уже существует")
            
    except Exception as e:
        print(f"❌ Ошибка при создании тестового супер администратора: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_super_admin()