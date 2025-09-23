import os
os.environ['ENCRYPTION_KEY'] = 'E6OEVs6c_KnDECL17YqWKjikmkMBqYyHhxriHQYCqtY='

import requests

# Test the run_bot endpoint
response = requests.post('http://localhost:8002/api/run_bot/testBot123/', json={'token': '123456789:ABCdefGHIjklMNOpqrSTUvwxYZ1234567890'})
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")