import os
import sys
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging to match main.py
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

# Test the function
bot_id = "mainBot"
token = get_bot_token(bot_id)
print(f"Token from main.py get_bot_token: {token}")

if token:
    print(f"Token found: {token[:10]}...{token[-5:]}")
else:
    print("No token found")