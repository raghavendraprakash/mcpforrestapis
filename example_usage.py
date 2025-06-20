#!/usr/bin/env python3
"""
Example usage of the Petstore MCP Client system
"""

import asyncio
import json
from agent_interface import PetstoreAgent
from client_config import ClientConfig


async def main():
    """Demonstrate the MCP client capabilities"""
    
    # Initialize the agent
    config = ClientConfig.default()
    agent = PetstoreAgent(config)
    
    print("=== Petstore MCP Client Demo ===\n")
    
    # Example 1: Find available pets
    print("1. Finding available pets...")
    try:
        result = await agent.execute_task("find_pets", status="available")
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Get prompt for pet search
    print("2. Getting prompt for pet search...")
    prompt = agent.get_prompt("pet_search", status="available", tags=["friendly"])
    print(f"System prompt: {prompt['system']}")
    print(f"User prompt: {prompt['user']}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 3: Get sampling configuration
    print("3. Getting sampling configuration...")
    sampling_config = agent.get_sampling_config("balanced")
    print(f"Sampling config: {json.dumps(sampling_config, indent=2)}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 4: Create a new pet
    print("4. Creating a new pet...")
    try:
        pet_data = {
            "name": "Buddy",
            "photoUrls": ["https://example.com/buddy.jpg"],
            "status": "available"
        }
        result = await agent.execute_task("manage_pet", action="add", **pet_data)
        print(f"Result: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nDemo completed!")


if __name__ == "__main__":
    asyncio.run(main())
