import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.db import db

def test_database_directly():
    # Connect to database
    if not db.connect():
        print("Failed to connect to database")
        return
    
    print("Connected to database successfully")
    
    # Check if bot ownership exists before deletion
    print("Checking bot ownership before deletion...")
    query = "SELECT user_id FROM bot_owners WHERE bot_id = %s"
    result = db.execute_query(query, ("test_endpoint_bot",))
    print(f"Bot ownership before deletion: {result}")
    
    # Try to delete bot ownership directly
    print("Deleting bot ownership directly...")
    delete_query = "DELETE FROM bot_owners WHERE bot_id = %s"
    delete_result = db.execute_update(delete_query, ("test_endpoint_bot",))
    print(f"Direct deletion result: {delete_result}")
    
    # Check if bot ownership exists after deletion
    print("Checking bot ownership after deletion...")
    result_after = db.execute_query(query, ("test_endpoint_bot",))
    print(f"Bot ownership after deletion: {result_after}")
    
    if result_after is None or len(result_after) == 0:
        print("SUCCESS: Bot ownership successfully deleted from database!")
    else:
        print("ERROR: Bot ownership still exists in database!")

if __name__ == "__main__":
    test_database_directly()