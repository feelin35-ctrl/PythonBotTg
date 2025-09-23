import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager

def test_bot_deletion():
    # Create user manager
    user_manager = UserManager()
    
    # Test creating a bot ownership
    print("Creating bot ownership...")
    result = user_manager.register_bot_ownership("test_user", "test_bot_123")
    print(f"Bot ownership creation result: {result}")
    
    # Check if bot ownership exists
    print("Checking bot ownership...")
    owner = user_manager.get_bot_owner("test_bot_123")
    print(f"Bot owner: {owner}")
    
    # Test deleting bot ownership
    print("Deleting bot ownership...")
    delete_result = user_manager.delete_bot_ownership("test_bot_123")
    print(f"Bot ownership deletion result: {delete_result}")
    
    # Check if bot ownership still exists
    print("Checking bot ownership after deletion...")
    owner_after = user_manager.get_bot_owner("test_bot_123")
    print(f"Bot owner after deletion: {owner_after}")
    
    if owner_after is None:
        print("SUCCESS: Bot ownership successfully deleted from database!")
    else:
        print("ERROR: Bot ownership still exists in database!")

if __name__ == "__main__":
    test_bot_deletion()