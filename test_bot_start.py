import os
import requests
import time

# Test starting the bot via the API
bot_id = "mainBot"

# Make sure the backend is running
try:
    response = requests.post(f'http://localhost:8002/api/run_bot/{bot_id}/', 
                           json={'token': ''})  # Empty token to force database lookup
    
    print(f"Response status code: {response.status_code}")
    print(f"Response data: {response.json()}")
    
except Exception as e:
    print(f"Error starting bot: {e}")