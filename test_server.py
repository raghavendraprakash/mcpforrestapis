#!/usr/bin/env python3
"""
Test script for the Petstore MCP Server
"""

import asyncio
import json
from petstore_mcp_server import make_api_request

async def test_api_endpoints():
    """Test various API endpoints"""
    
    print("Testing Petstore API endpoints...")
    
    # Test getting inventory
    try:
        print("\n1. Testing get inventory...")
        inventory = await make_api_request("GET", "/store/inventory")
        print(f"Inventory: {json.dumps(inventory, indent=2)}")
    except Exception as e:
        print(f"Error getting inventory: {e}")
    
    # Test finding pets by status
    try:
        print("\n2. Testing find pets by status...")
        pets = await make_api_request("GET", "/pet/findByStatus", params={"status": "available"})
        print(f"Found {len(pets) if isinstance(pets, list) else 'unknown'} available pets")
        if isinstance(pets, list) and pets:
            print(f"First pet: {json.dumps(pets[0], indent=2)}")
    except Exception as e:
        print(f"Error finding pets: {e}")
    
    # Test user login (this might fail without valid credentials)
    try:
        print("\n3. Testing user login...")
        login_result = await make_api_request("GET", "/user/login", params={"username": "test", "password": "test"})
        print(f"Login result: {json.dumps(login_result, indent=2)}")
    except Exception as e:
        print(f"Error logging in (expected): {e}")
    
    print("\nAPI tests completed!")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())
