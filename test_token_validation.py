import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

from main import validate_telegram_token, check_token_sync

# Test with a valid token format
test_token = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij"
print(f"Validate token: {validate_telegram_token(test_token)}")

# Test with our test token
test_token2 = "123456789:ABCdefGHIjklMNOpqrSTUvwxYZ1234567890"
print(f"Validate test token: {validate_telegram_token(test_token2)}")

# Test with an invalid token
invalid_token = "invalid_token"
print(f"Validate invalid token: {validate_telegram_token(invalid_token)}")