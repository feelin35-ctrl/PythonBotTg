import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from main import get_bot_token, validate_telegram_token, check_token_sync

# Test retrieving the token for mainBot
bot_id = "mainBot"
token = get_bot_token(bot_id)

print(f"Retrieved token: {token}")

if token:
    print(f"Token length: {len(token)}")
    print(f"Token format validation: {validate_telegram_token(token)}")
    
    # Check if it's a test token
    is_test_token = token.startswith("123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ") or token == "8495785437:AAFR_fwx0AlVTcVanFMwZ7Uf5Z4t3Sk-YdA"
    print(f"Is test token: {is_test_token}")
    
    # Test token validation
    print(f"Token sync validation: {check_token_sync(token)}")
else:
    print(f"Failed to retrieve token for bot {bot_id}")