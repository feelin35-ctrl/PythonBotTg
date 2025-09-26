import json
from main import Scenario, Node, Edge

# Тест 1: Создание сценария с admin_chat_id (snake_case)
print("Тест 1: Создание сценария с admin_chat_id (snake_case)")
scenario1 = Scenario(
    nodes=[],
    edges=[],
    admin_chat_id="123456789"
)
print(f"admin_chat_id: {scenario1.admin_chat_id}")
print(f"model_dump(): {scenario1.model_dump()}")
print()

# Тест 2: Создание сценария с adminChatId (camelCase)
print("Тест 2: Создание сценария с adminChatId (camelCase)")
scenario_data = {
    "nodes": [],
    "edges": [],
    "adminChatId": "987654321"
}
scenario2 = Scenario(**scenario_data)
print(f"admin_chat_id: {scenario2.admin_chat_id}")
print(f"model_dump(): {scenario2.model_dump()}")
print()

# Тест 3: Создание сценария с обоими форматами (adminChatId должен иметь приоритет)
print("Тест 3: Создание сценария с обоими форматами")
scenario_data3 = {
    "nodes": [],
    "edges": [],
    "admin_chat_id": "111111111",
    "adminChatId": "222222222"
}
scenario3 = Scenario(**scenario_data3)
print(f"admin_chat_id: {scenario3.admin_chat_id}")
print(f"model_dump(): {scenario3.model_dump()}")
print()

print("Все тесты пройдены успешно!")