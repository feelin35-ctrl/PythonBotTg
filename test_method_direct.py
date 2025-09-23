import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.models import UserManager
from core.db import db

def test_method_directly():
    # Connect to database
    if not db.connect():
        print("Failed to connect to database")
        return
    
    # Create a test bot ownership first
    print("Creating test bot ownership...")
    user_manager = UserManager()
    result = user_manager.register_bot_ownership("1", "direct_test_bot")
    print(f"Bot ownership creation result: {result}")
    
    # Check if it exists
    print("Checking if bot ownership exists...")
    query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
    result_check = db.execute_query(query, ("direct_test_bot",))
    print(f"Bot ownership check result: {result_check}")
    
    # Now test the delete method directly
    print("Testing delete method directly...")
    delete_result = user_manager.delete_bot_ownership("direct_test_bot")
    print(f"Delete method result: {delete_result}")
    
    # Check if it was deleted
    print("Checking if bot ownership was deleted...")
    result_after = db.execute_query(query, ("direct_test_bot",))
    print(f"Bot ownership after deletion: {result_after}")
    
    if result_after is None or len(result_after) == 0:
        print("SUCCESS: Bot ownership successfully deleted!")
    else:
        print("ERROR: Bot ownership still exists!")

if __name__ == "__main__":
    test_method_directly()