#!/usr/bin/env python3
"""
Тестовый скрипт для проверки фильтрации ботов по пользователям
"""

import requests
import json

def test_user_bots():
    """Тестирует фильтрацию ботов по пользователям"""
    
    # Тестируем разных пользователей
    users = [
        {"id": "1", "name": "admin"},
        {"id": "3", "name": "testuser"},
        {"id": "6", "name": "testuser2"},
        {"id": "7", "name": "Feelin35"},
        {"id": "8", "name": "Feelin"}
    ]
    
    print("=== Тест фильтрации ботов по пользователям ===\n")
    
    # Тест без пользователя (анонимный доступ)
    print("1. Анонимный доступ (без user_id):")
    try:
        response = requests.get("http://localhost:8001/api/get_bots/")
        bots = response.json().get("bots", [])
        print(f"   Ботов видно: {len(bots)}")
        if bots:
            for bot in bots:
                print(f"     - {bot}")
        else:
            print("   Нет доступных ботов (как и должно быть)")
    except Exception as e:
        print(f"   Ошибка: {e}")
    
    print()
    
    # Тест с разными пользователями
    for i, user in enumerate(users, 2):
        print(f"{i}. Пользователь {user['name']} (ID {user['id']}):")
        try:
            response = requests.get(f"http://localhost:8001/api/get_bots/?user_id={user['id']}")
            bots = response.json().get("bots", [])
            print(f"   Ботов видно: {len(bots)}")
            if bots:
                for bot in bots:
                    print(f"     - {bot}")
            else:
                print("   Нет ботов")
        except Exception as e:
            print(f"   Ошибка: {e}")
        print()

if __name__ == "__main__":
    test_user_bots()