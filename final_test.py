import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import the actual get_bot_token function from main.py
from main import get_bot_token

def test_token_retrieval():
    """Test that tokens are retrieved correctly from the database"""
    print("Testing token retrieval from database...")
    
    # Test with mainBot
    bot_id = "mainBot"
    token = get_bot_token(bot_id)
    
    if token:
        print(f"✅ SUCCESS: Token found for {bot_id}")
        print(f"   Token: {token[:10]}...{token[-5:]}")
        return True
    else:
        print(f"❌ FAILED: No token found for {bot_id}")
        return False

def test_no_token_file():
    """Test that there's no token file being used"""
    token_file = "bot_tokens.json"
    if os.path.exists(token_file):
        print(f"❌ FAILED: Token file {token_file} still exists")
        return False
    else:
        print(f"✅ SUCCESS: Token file {token_file} does not exist")
        return True

if __name__ == "__main__":
    print("Running final tests...\n")
    
    test1_passed = test_token_retrieval()
    test2_passed = test_no_token_file()
    
    print("\n" + "="*50)
    if test1_passed and test2_passed:
        print("✅ ALL TESTS PASSED: System is working correctly without token file")
    else:
        print("❌ SOME TESTS FAILED: Please check the implementation")
    print("="*50)