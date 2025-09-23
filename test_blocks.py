import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.block_registry import block_registry

def test_available_blocks():
    """Тест для проверки доступных блоков"""
    print("Проверка доступных блоков...")
    print("=" * 50)
    
    # Получаем список доступных блоков
    blocks = block_registry.get_available_blocks()
    
    print("Доступные блоки:")
    for block in blocks:
        print(f"  - {block}")
    
    print(f"\nВсего блоков: {len(blocks)}")
    
    # Проверяем, что блоки contextual_nlp и advanced_contextual_nlp отсутствуют
    unexpected_blocks = ["contextual_nlp", "advanced_contextual_nlp"]
    
    print("\nПроверка удаленных блоков:")
    for block_type in unexpected_blocks:
        if block_type in blocks:
            print(f"  ❌ {block_type} - НЕ ДОЛЖЕН БЫТЬ НАЙДЕН")
        else:
            print(f"  ✅ {block_type} - успешно удален")
    
    print("=" * 50)

if __name__ == "__main__":
    test_available_blocks()