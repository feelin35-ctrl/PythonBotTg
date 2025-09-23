import requests
import json

# Test the API directly
try:
    # Test without user_id (should return all bots)
    response = requests.get('http://localhost:8001/api/get_bots/')
    print("Response without user_id:")
    print(response.json())
    
    print("\n" + "="*50 + "\n")
    
    # Test with user_id=3 (testuser - should return only user's bots)
    response = requests.get('http://localhost:8001/api/get_bots/', params={'user_id': '3'})
    print("Response with user_id=3:")
    print(response.json())
    
    print("\n" + "="*50 + "\n")
    
    # Test with user_id=6 (testuser2 - should return only user's bots)
    response = requests.get('http://localhost:8001/api/get_bots/', params={'user_id': '6'})
    print("Response with user_id=6:")
    print(response.json())
    
except Exception as e:
    print(f"Error: {e}")