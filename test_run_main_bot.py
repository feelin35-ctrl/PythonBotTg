import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

import requests

# Test the run_bot endpoint for mainBot
response = requests.post('http://localhost:8002/api/run_bot/mainBot/', json={'token': '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghij'})
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")