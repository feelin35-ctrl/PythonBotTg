import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

def create_super_admin(username, email, password):
    """Создает супер администратора"""
    try:
        user_manager = UserManager()
        
        # Регистрируем пользователя с правами супер администратора
        success = user_manager.register_user(username, email, password, role="super_admin")
        
        if success:
            print(f"✅ Супер администратор '{username}' успешно создан")
            print(f"Email: {email}")
            print("Теперь этот пользователь может видеть всех ботов в системе")
        else:
            print(f"❌ Не удалось создать супер администратора '{username}'")
            print("Возможно, пользователь с таким именем или email уже существует")
            
    except Exception as e:
        print(f"❌ Ошибка при создании супер администратора: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Запрашиваем данные у пользователя
    print("Создание супер администратора")
    print("=" * 30)
    
    username = input("Введите имя пользователя: ").strip()
    email = input("Введите email: ").strip()
    password = input("Введите пароль: ").strip()
    
    if username and email and password:
        create_super_admin(username, email, password)
    else:
        print("❌ Все поля должны быть заполнены")