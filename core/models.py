from pydantic import BaseModel
from typing import Optional, Dict, List
import json
import os
import hashlib
from datetime import datetime
from core.db import db

class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    password_hash: str
    role: str = "admin"  # Default role is admin
    created_at: str = datetime.now().isoformat()
    last_login: Optional[str] = None

class UserToken(BaseModel):
    user_id: str
    bot_id: str
    token: str  # Будет храниться в зашифрованном виде
    created_at: str = datetime.now().isoformat()

class UserManager:
    def __init__(self):
        # Initialize database connection
        if not db.connect():
            raise Exception("Failed to connect to database")
        
        # Create tables if they don't exist
        if not db.create_tables():
            raise Exception("Failed to create database tables")
    
    def hash_password(self, password: str) -> str:
        """Хеширует пароль"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, email: str, password: str, role: str = "admin") -> bool:
        """Регистрирует нового пользователя с указанной ролью"""
        try:
            # Check if user already exists
            query = "SELECT id FROM users WHERE username = %s OR email = %s"
            result = db.execute_query(query, (username, email))
            
            if result and len(result) > 0:
                return False  # User already exists
            
            # Insert new user
            password_hash = self.hash_password(password)
            created_at = datetime.now().isoformat()
            query = """
                INSERT INTO users (username, email, password_hash, role, created_at) 
                VALUES (%s, %s, %s, %s, %s)
            """
            result = db.execute_update(query, (username, email, password_hash, role, created_at))
            
            return result is not None and result > 0
        except Exception as e:
            print(f"Ошибка регистрации пользователя: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Аутентифицирует пользователя"""
        try:
            # Сначала находим пользователя по имени
            query = "SELECT id, username, email, password_hash, role, created_at, last_login FROM users WHERE username = %s"
            result = db.execute_query(query, (username,))
            
            if result and len(result) > 0:
                user_data = result[0]
                stored_password_hash = user_data[3]
                
                # Хешируем введенный пароль и сравниваем с хешем из базы
                input_password_hash = self.hash_password(password)
                
                if input_password_hash == stored_password_hash:
                    # Update last login time
                    update_query = "UPDATE users SET last_login = %s WHERE id = %s"
                    db.execute_update(update_query, (datetime.now().isoformat(), user_data[0]))
                    
                    # Создаем объект пользователя с ID
                    user = User(
                        id=str(user_data[0]),  # Сохраняем ID пользователя
                        username=user_data[1],
                        email=user_data[2],
                        password_hash=user_data[3],
                        role=user_data[4],  # Role instead of is_admin
                        created_at=str(user_data[5]),  # Преобразуем в строку
                        last_login=datetime.now().isoformat()
                    )
                    return user
            return None
        except Exception as e:
            print(f"Ошибка аутентификации пользователя: {e}")
            return None
    
    def save_user_token(self, user_id: str, bot_id: str, token: str) -> bool:
        """Сохраняет токен для пользователя"""
        try:
            from core.security import encrypt_token
            encrypted_token = encrypt_token(token)
            
            # Check if token already exists for this user and bot
            query = "SELECT id FROM user_tokens WHERE user_id = %s AND bot_id = %s"
            result = db.execute_query(query, (user_id, bot_id))
            
            if result and len(result) > 0:
                # Update existing token
                update_query = "UPDATE user_tokens SET token = %s, created_at = %s WHERE user_id = %s AND bot_id = %s"
                result = db.execute_update(update_query, (encrypted_token, datetime.now().isoformat(), user_id, bot_id))
            else:
                # Insert new token
                query = "INSERT INTO user_tokens (user_id, bot_id, token, created_at) VALUES (%s, %s, %s, %s)"
                result = db.execute_update(query, (user_id, bot_id, encrypted_token, datetime.now().isoformat()))
            
            # Also register bot ownership
            self.register_bot_ownership(user_id, bot_id)
            
            return result is not None and result > 0
        except Exception as e:
            print(f"Ошибка сохранения токена пользователя: {e}")
            return False
    
    def get_user_token(self, user_id: str, bot_id: str) -> Optional[str]:
        """Получает токен пользователя"""
        try:
            query = "SELECT token FROM user_tokens WHERE user_id = %s AND bot_id = %s"
            result = db.execute_query(query, (user_id, bot_id))
            
            if result and len(result) > 0:
                from core.security import decrypt_token
                return decrypt_token(result[0][0])
            return None
        except Exception as e:
            print(f"Ошибка получения токена пользователя: {e}")
            return None
    
    def delete_user_token(self, user_id: str, bot_id: str) -> bool:
        """Удаляет токен пользователя"""
        try:
            query = "DELETE FROM user_tokens WHERE user_id = %s AND bot_id = %s"
            result = db.execute_update(query, (user_id, bot_id))
            return result is not None and result > 0
        except Exception as e:
            print(f"Ошибка удаления токена пользователя: {e}")
            return False
    
    def register_bot_ownership(self, user_id: str, bot_id: str) -> bool:
        """Регистрирует право собственности пользователя на бота"""
        try:
            print(f"Attempting to register bot ownership: user_id={user_id}, bot_id={bot_id}")
            
            # Check if bot ownership already exists
            query = "SELECT id FROM bot_owners WHERE bot_id = %s"
            result = db.execute_query(query, (bot_id,))
            print(f"Existing ownership check result: {result}")
            
            if result and len(result) > 0:
                print(f"Updating existing ownership for bot {bot_id}")
                # Update existing ownership
                update_query = "UPDATE bot_owners SET user_id = %s, created_at = %s WHERE bot_id = %s"
                result = db.execute_update(update_query, (user_id, datetime.now().isoformat(), bot_id))
                print(f"Update result: {result}")
            else:
                print(f"Inserting new ownership for bot {bot_id}")
                # Insert new ownership
                query = "INSERT INTO bot_owners (user_id, bot_id, created_at) VALUES (%s, %s, %s)"
                result = db.execute_update(query, (user_id, bot_id, datetime.now().isoformat()))
                print(f"Insert result: {result}")
            
            success = result is not None and result > 0
            print(f"Ownership registration successful: {success}")
            return success
        except Exception as e:
            print(f"Ошибка регистрации права собственности на бота: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_user_bots(self, user_id: str) -> List[str]:
        """Получает список ботов, принадлежащих пользователю"""
        try:
            query = "SELECT bot_id FROM bot_owners WHERE user_id = %s"
            result = db.execute_query(query, (user_id,))
            
            print(f"get_user_bots query result for user_id {user_id}: {result}")
            
            if result:
                bots = [row[0] for row in result]
                print(f"Returning bots list: {bots}")
                return bots
            print("No bots found for user")
            return []
        except Exception as e:
            print(f"Ошибка получения списка ботов пользователя: {e}")
            return []
    
    def get_bot_owner(self, bot_id: str) -> Optional[str]:
        """Получает ID владельца бота"""
        try:
            query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
            result = db.execute_query(query, (bot_id,))
            
            if result and len(result) > 0:
                return str(result[0][0])
            return None
        except Exception as e:
            print(f"Ошибка получения владельца бота: {e}")
            return None
    
    def get_all_bots_with_owners(self) -> Dict[str, str]:
        """Получает все боты с их владельцами"""
        try:
            query = "SELECT bot_id, user_id FROM bot_owners"
            result = db.execute_query(query, ())
            
            bot_owners = {}
            if result:
                for row in result:
                    bot_id, user_id = row
                    bot_owners[bot_id] = str(user_id)
            return bot_owners
        except Exception as e:
            print(f"Ошибка получения всех ботов с владельцами: {e}")
            return {}

    def delete_bot_ownership(self, bot_id: str) -> bool:
        """Удаляет информацию о праве собственности на бота"""
        try:
            print(f"Attempting to delete bot ownership for bot_id: {bot_id}")
            query = "DELETE FROM bot_owners WHERE bot_id = %s"
            result = db.execute_update(query, (bot_id,))
            print(f"Delete query result: {result}")
            # The operation is successful if result is not None (no database error)
            # Even if result is 0 (no rows deleted), it's still a successful operation
            success = result is not None
            print(f"Delete operation success: {success}")
            return success
        except Exception as e:
            print(f"Ошибка удаления права собственности на бота: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_users(self) -> List[Dict]:
        """Получает список всех пользователей (только для super_admin)"""
        try:
            query = "SELECT id, username, email, role, created_at, last_login FROM users"
            result = db.execute_query(query, ())
            
            users = []
            if result:
                for row in result:
                    users.append({
                        "id": str(row[0]),
                        "username": row[1],
                        "email": row[2],
                        "role": row[3],
                        "created_at": str(row[4]),
                        "last_login": str(row[5]) if row[5] else None
                    })
            return users
        except Exception as e:
            print(f"Ошибка получения списка всех пользователей: {e}")
            return []
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Получает пользователя по ID"""
        try:
            query = "SELECT id, username, email, password_hash, role, created_at, last_login FROM users WHERE id = %s"
            result = db.execute_query(query, (user_id,))
            
            if result and len(result) > 0:
                user_data = result[0]
                user = User(
                    id=str(user_data[0]),
                    username=user_data[1],
                    email=user_data[2],
                    password_hash=user_data[3],
                    role=user_data[4],
                    created_at=str(user_data[5]),
                    last_login=str(user_data[6]) if user_data[6] else None
                )
                return user
            return None
        except Exception as e:
            print(f"Ошибка получения пользователя по ID: {e}")
            return None
    
    def update_user_role(self, user_id: str, new_role: str, updated_by_user_id: str) -> bool:
        """Обновляет роль пользователя (только super_admin может назначать super_admin)"""
        try:
            # First check if the user requesting the update is a super_admin
            query = "SELECT role FROM users WHERE id = %s"
            result = db.execute_query(query, (updated_by_user_id,))
            
            if not result or len(result) == 0:
                print("User requesting role update not found")
                return False
                
            requesting_user_role = result[0][0]
            
            # Only super_admin can update roles
            if requesting_user_role != "super_admin":
                print("Only super_admin can update user roles")
                return False
            
            # Only super_admin can assign super_admin role
            if new_role == "super_admin" and requesting_user_role != "super_admin":
                print("Only super_admin can assign super_admin role")
                return False
            
            # Update the user's role
            update_query = "UPDATE users SET role = %s WHERE id = %s"
            result = db.execute_update(update_query, (new_role, user_id))
            
            return result is not None and result > 0
        except Exception as e:
            print(f"Ошибка обновления роли пользователя: {e}")
            return False
    
    def is_super_admin(self, user_id: str) -> bool:
        """Проверяет, является ли пользователь суперадминистратором"""
        try:
            query = "SELECT role FROM users WHERE id = %s"
            result = db.execute_query(query, (user_id,))
            
            if result and len(result) > 0:
                return result[0][0] == "super_admin"
            return False
        except Exception as e:
            print(f"Ошибка проверки роли пользователя: {e}")
            return False
    
    def get_all_bots_for_super_admin(self) -> List[str]:
        """Получает все боты в системе (только для super_admin)"""
        try:
            query = "SELECT bot_id FROM bot_owners"
            result = db.execute_query(query, ())
            
            if result:
                return [row[0] for row in result]
            return []
        except Exception as e:
            print(f"Ошибка получения всех ботов для super_admin: {e}")
            return []

    def delete_user_and_associated_data(self, user_id: str, deleted_by_user_id: str) -> bool:
        """Удаляет пользователя и всю связанную с ним информацию (только для super_admin)
        
        Args:
            user_id (str): ID пользователя, которого нужно удалить
            deleted_by_user_id (str): ID пользователя, который выполняет удаление (должен быть super_admin)
            
        Returns:
            bool: True если пользователь успешно удален, False в противном случае
            
        Example:
            # Удаление пользователя с ID "3" суперадмином с ID "1"
            success = user_manager.delete_user_and_associated_data("3", "1")
            
        Note:
            Эта функция удаляет:
            - Самого пользователя из таблицы users
            - Все токены пользователя из таблицы user_tokens
            - Все боты пользователя и их сценарии
            - Все записи о владении ботами из таблицы bot_owners
            
        Implementation Details:
            1. Проверяет, что пользователь, выполняющий удаление, имеет роль super_admin
            2. Получает список всех ботов пользователя
            3. Для каждого бота:
               - Удаляет запись о владении ботом из таблицы bot_owners
               - Удаляет токен бота из таблицы user_tokens
               - Удаляет файл сценария бота (если существует)
            4. Удаляет все токены пользователя
            5. Удаляет самого пользователя из таблицы users
            
        API Usage:
            Для использования через API, отправьте DELETE запрос на:
            DELETE /api/user/{user_id}/?deleted_by_user_id={deleted_by_user_id}
            
            Пример cURL:
            curl -X DELETE "http://localhost:8003/api/user/USER_ID?deleted_by_user_id=SUPER_ADMIN_ID" \\
                 -H "Content-Type: application/json"
                 
            Пример JavaScript:
            fetch('http://localhost:8003/api/user/USER_ID?deleted_by_user_id=SUPER_ADMIN_ID', {
              method: 'DELETE',
              headers: {
                'Content-Type': 'application/json',
              }
            })
        """
        try:
            # First check if the user requesting the deletion is a super_admin
            query = "SELECT role FROM users WHERE id = %s"
            result = db.execute_query(query, (deleted_by_user_id,))
            
            if not result or len(result) == 0:
                print("User requesting deletion not found")
                return False
                
            requesting_user_role = result[0][0]
            
            # Only super_admin can delete users
            if requesting_user_role != "super_admin":
                print("Only super_admin can delete users")
                return False
            
            # Get all bots owned by the user
            user_bots = self.get_user_bots(user_id)
            print(f"User {user_id} owns bots: {user_bots}")
            
            # Delete all bots and their associated data
            for bot_id in user_bots:
                print(f"Deleting bot {bot_id} and associated data...")
                
                # Delete bot ownership record
                self.delete_bot_ownership(bot_id)
                
                # Delete bot token if exists
                try:
                    delete_token_query = "DELETE FROM user_tokens WHERE user_id = %s AND bot_id = %s"
                    db.execute_update(delete_token_query, (user_id, bot_id))
                    print(f"Deleted token for bot {bot_id}")
                except Exception as e:
                    print(f"Error deleting token for bot {bot_id}: {e}")
                
                # Delete bot scenario file if exists
                try:
                    from main import bot_file
                    import os
                    # Получаем владельца бота для определения правильного пути
                    bot_owner = self.get_bot_owner(bot_id)
                    if bot_owner:
                        bot_file_path = bot_file(bot_id, bot_owner)
                        if os.path.exists(bot_file_path):
                            os.remove(bot_file_path)
                            print(f"Deleted bot scenario file: {bot_file_path}")
                    else:
                        print(f"Could not determine owner for bot {bot_id}")
                except Exception as e:
                    print(f"Error deleting bot scenario file for bot {bot_id}: {e}")
            
            # Delete all user tokens
            try:
                delete_all_tokens_query = "DELETE FROM user_tokens WHERE user_id = %s"
                db.execute_update(delete_all_tokens_query, (user_id,))
                print(f"Deleted all tokens for user {user_id}")
            except Exception as e:
                print(f"Error deleting user tokens: {e}")
            
            # Finally, delete the user
            delete_user_query = "DELETE FROM users WHERE id = %s"
            result = db.execute_update(delete_user_query, (user_id,))
            
            success = result is not None and result > 0
            if success:
                print(f"User {user_id} and all associated data successfully deleted")
            else:
                print(f"Failed to delete user {user_id}")
            
            return success
        except Exception as e:
            print(f"Ошибка удаления пользователя и связанных данных: {e}")
            import traceback
            traceback.print_exc()
            return False
