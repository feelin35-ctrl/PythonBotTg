import mysql.connector
import os
from mysql.connector import Error
import logging
from typing import Optional, List, Tuple, Any

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
    
    def connect(self) -> bool:
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'telegram_bot_builder'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                port=int(os.getenv('DB_PORT', 3306))
            )
            
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                logger.info("Successfully connected to MySQL database")
                return True
            else:
                return False
                
        except Error as e:
            logger.error(f"Error while connecting to MySQL: {e}")
            return False
    
    def disconnect(self) -> None:
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            logger.info("MySQL connection is closed")
    
    def create_tables(self) -> bool:
        """Create necessary tables if they don't exist"""
        if not self.connection or not self.cursor:
            logger.error("Database not connected")
            return False
            
        try:
            # Create users table with role support
            create_users_table = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('super_admin', 'admin') DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
            """
            
            # Create user_tokens table
            create_tokens_table = """
            CREATE TABLE IF NOT EXISTS user_tokens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                bot_id VARCHAR(100) NOT NULL,
                token TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_bot (user_id, bot_id)
            )
            """
            
            # Create bot_owners table to track bot ownership
            create_bot_owners_table = """
            CREATE TABLE IF NOT EXISTS bot_owners (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                bot_id VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                UNIQUE KEY unique_bot (bot_id)
            )
            """
            
            self.cursor.execute(create_users_table)
            self.cursor.execute(create_tokens_table)
            self.cursor.execute(create_bot_owners_table)
            self.connection.commit()
            
            logger.info("Database tables created successfully")
            return True
            
        except Error as e:
            logger.error(f"Error creating tables: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> Any:
        """Execute a SELECT query"""
        if not self.cursor:
            logger.error("Database not connected")
            return None
            
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"Error executing query: {e}")
            return None
    
    def execute_update(self, query: str, params: Optional[Tuple] = None) -> Optional[int]:
        """Execute an INSERT, UPDATE, or DELETE query"""
        if not self.connection or not self.cursor:
            logger.error("Database not connected")
            return None
            
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.rowcount
        except Error as e:
            logger.error(f"Error executing update: {e}")
            self.connection.rollback()
            return None

# Global database instance
db = Database()