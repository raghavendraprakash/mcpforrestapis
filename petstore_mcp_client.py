#!/usr/bin/env python3
"""
Petstore MCP Client

A comprehensive MCP client for interacting with the Petstore MCP server.
Provides high-level methods for agents to seamlessly use all Petstore API functionality.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("petstore-mcp-client")


class PetstoreClient:
    """High-level client for interacting with the Petstore MCP server"""
    
    def __init__(self, server_path: str = "./petstore-mcp-server.py"):
        """Initialize the Petstore client
        
        Args:
            server_path: Path to the MCP server executable
        """
        self.server_path = server_path
        self.session: Optional[ClientSession] = None
        self._server_params = StdioServerParameters(
            command="python3",
            args=[server_path],
            env=None
        )
    
    @asynccontextmanager
    async def connect(self):
        """Context manager for connecting to the MCP server"""
        async with stdio_client(self._server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                
                # Initialize the session
                await session.initialize()
                
                # List available tools for verification
                tools = await session.list_tools()
                logger.info(f"Connected to Petstore MCP server with {len(tools.tools)} tools")
                
                yield self
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to call MCP tools"""
        if not self.session:
            raise RuntimeError("Client not connected. Use 'async with client.connect():'")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            # Extract text content from the result
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    response_text = content.text
                    
                    # Try to parse JSON if it looks like structured data
                    if response_text.strip().startswith('{') or response_text.strip().startswith('['):
                        try:
                            # Extract JSON from the response text
                            json_start = response_text.find('{')
                            if json_start == -1:
                                json_start = response_text.find('[')
                            
                            if json_start != -1:
                                json_text = response_text[json_start:]
                                return json.loads(json_text)
                        except json.JSONDecodeError:
                            pass
                    
                    return {"message": response_text}
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            return {"error": str(e)}
    
    # Pet Management Methods
    
    async def add_pet(self, name: str, photo_urls: List[str], 
                     category: Optional[Dict[str, Any]] = None,
                     tags: Optional[List[Dict[str, Any]]] = None,
                     status: str = "available") -> Dict[str, Any]:
        """Add a new pet to the store
        
        Args:
            name: Pet name
            photo_urls: List of photo URLs
            category: Pet category (optional)
            tags: List of tags (optional)
            status: Pet status (available, pending, sold)
        
        Returns:
            API response with pet data
        """
        pet_data = {
            "name": name,
            "photoUrls": photo_urls,
            "status": status
        }
        
        if category:
            pet_data["category"] = category
        if tags:
            pet_data["tags"] = tags
        
        return await self._call_tool("add_pet", {"pet": pet_data})
    
    async def update_pet(self, pet_id: int, name: str, photo_urls: List[str],
                        category: Optional[Dict[str, Any]] = None,
                        tags: Optional[List[Dict[str, Any]]] = None,
                        status: str = "available") -> Dict[str, Any]:
        """Update an existing pet
        
        Args:
            pet_id: Pet ID
            name: Pet name
            photo_urls: List of photo URLs
            category: Pet category (optional)
            tags: List of tags (optional)
            status: Pet status
        
        Returns:
            API response with updated pet data
        """
        pet_data = {
            "id": pet_id,
            "name": name,
            "photoUrls": photo_urls,
            "status": status
        }
        
        if category:
            pet_data["category"] = category
        if tags:
            pet_data["tags"] = tags
        
        return await self._call_tool("update_pet", {"pet": pet_data})
    
    async def get_pet_by_id(self, pet_id: int) -> Dict[str, Any]:
        """Get pet by ID
        
        Args:
            pet_id: Pet ID
        
        Returns:
            Pet data
        """
        return await self._call_tool("get_pet_by_id", {"pet_id": pet_id})
    
    async def find_pets_by_status(self, status: str = "available") -> Dict[str, Any]:
        """Find pets by status
        
        Args:
            status: Pet status (available, pending, sold)
        
        Returns:
            List of pets matching the status
        """
        return await self._call_tool("find_pets_by_status", {"status": status})
    
    async def find_pets_by_tags(self, tags: List[str]) -> Dict[str, Any]:
        """Find pets by tags
        
        Args:
            tags: List of tag names
        
        Returns:
            List of pets matching the tags
        """
        return await self._call_tool("find_pets_by_tags", {"tags": tags})
    
    async def update_pet_with_form(self, pet_id: int, name: Optional[str] = None,
                                  status: Optional[str] = None) -> Dict[str, Any]:
        """Update pet with form data
        
        Args:
            pet_id: Pet ID
            name: New pet name (optional)
            status: New pet status (optional)
        
        Returns:
            Updated pet data
        """
        args = {"pet_id": pet_id}
        if name:
            args["name"] = name
        if status:
            args["status"] = status
        
        return await self._call_tool("update_pet_with_form", args)
    
    async def delete_pet(self, pet_id: int, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Delete a pet
        
        Args:
            pet_id: Pet ID
            api_key: API key for authentication (optional)
        
        Returns:
            Deletion confirmation
        """
        args = {"pet_id": pet_id}
        if api_key:
            args["api_key"] = api_key
        
        return await self._call_tool("delete_pet", args)
    
    async def upload_pet_image(self, pet_id: int, 
                              additional_metadata: Optional[str] = None) -> Dict[str, Any]:
        """Upload an image for a pet
        
        Args:
            pet_id: Pet ID
            additional_metadata: Additional metadata (optional)
        
        Returns:
            Upload response
        """
        args = {"pet_id": pet_id}
        if additional_metadata:
            args["additional_metadata"] = additional_metadata
        
        return await self._call_tool("upload_pet_image", args)
    
    # Store Operations Methods
    
    async def get_inventory(self) -> Dict[str, Any]:
        """Get pet inventories by status
        
        Returns:
            Inventory data with status counts
        """
        return await self._call_tool("get_inventory", {})
    
    async def place_order(self, pet_id: int, quantity: int = 1,
                         ship_date: Optional[str] = None,
                         status: str = "placed",
                         complete: bool = False) -> Dict[str, Any]:
        """Place an order for a pet
        
        Args:
            pet_id: Pet ID
            quantity: Order quantity
            ship_date: Shipping date (ISO format)
            status: Order status (placed, approved, delivered)
            complete: Whether order is complete
        
        Returns:
            Order data
        """
        order_data = {
            "petId": pet_id,
            "quantity": quantity,
            "status": status,
            "complete": complete
        }
        
        if ship_date:
            order_data["shipDate"] = ship_date
        
        return await self._call_tool("place_order", {"order": order_data})
    
    async def get_order_by_id(self, order_id: int) -> Dict[str, Any]:
        """Get order by ID
        
        Args:
            order_id: Order ID
        
        Returns:
            Order data
        """
        return await self._call_tool("get_order_by_id", {"order_id": order_id})
    
    async def delete_order(self, order_id: int) -> Dict[str, Any]:
        """Delete order by ID
        
        Args:
            order_id: Order ID
        
        Returns:
            Deletion confirmation
        """
        return await self._call_tool("delete_order", {"order_id": order_id})
    
    # User Management Methods
    
    async def create_user(self, username: str, first_name: str, last_name: str,
                         email: str, password: str, phone: Optional[str] = None,
                         user_status: int = 1) -> Dict[str, Any]:
        """Create a new user
        
        Args:
            username: Username
            first_name: First name
            last_name: Last name
            email: Email address
            password: Password
            phone: Phone number (optional)
            user_status: User status
        
        Returns:
            Created user data
        """
        user_data = {
            "username": username,
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "password": password,
            "userStatus": user_status
        }
        
        if phone:
            user_data["phone"] = phone
        
        return await self._call_tool("create_user", {"user": user_data})
    
    async def create_users_with_list(self, users: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create multiple users from a list
        
        Args:
            users: List of user data dictionaries
        
        Returns:
            Creation response
        """
        return await self._call_tool("create_users_with_list", {"users": users})
    
    async def login_user(self, username: str, password: str) -> Dict[str, Any]:
        """Log user into the system
        
        Args:
            username: Username
            password: Password
        
        Returns:
            Login response with session info
        """
        return await self._call_tool("login_user", {
            "username": username,
            "password": password
        })
    
    async def logout_user(self) -> Dict[str, Any]:
        """Log out current user session
        
        Returns:
            Logout confirmation
        """
        return await self._call_tool("logout_user", {})
    
    async def get_user_by_name(self, username: str) -> Dict[str, Any]:
        """Get user by username
        
        Args:
            username: Username
        
        Returns:
            User data
        """
        return await self._call_tool("get_user_by_name", {"username": username})
    
    async def update_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user information
        
        Args:
            username: Username to update
            user_data: Updated user data
        
        Returns:
            Update confirmation
        """
        return await self._call_tool("update_user", {
            "username": username,
            "user": user_data
        })
    
    async def delete_user(self, username: str) -> Dict[str, Any]:
        """Delete a user
        
        Args:
            username: Username to delete
        
        Returns:
            Deletion confirmation
        """
        return await self._call_tool("delete_user", {"username": username})
    
    # High-level convenience methods for agents
    
    async def search_available_pets(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search for available pets, optionally filtered by tags
        
        Args:
            tags: Optional list of tags to filter by
        
        Returns:
            List of available pets
        """
        if tags:
            result = await self.find_pets_by_tags(tags)
        else:
            result = await self.find_pets_by_status("available")
        
        # Extract pets from the response
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and "pets" in result:
            return result["pets"]
        else:
            return []
    
    async def create_pet_with_category(self, name: str, photo_urls: List[str],
                                     category_name: str, tag_names: List[str] = None) -> Dict[str, Any]:
        """Create a pet with category and tags
        
        Args:
            name: Pet name
            photo_urls: List of photo URLs
            category_name: Category name
            tag_names: List of tag names
        
        Returns:
            Created pet data
        """
        category = {"id": 1, "name": category_name}
        tags = []
        
        if tag_names:
            for i, tag_name in enumerate(tag_names):
                tags.append({"id": i + 1, "name": tag_name})
        
        return await self.add_pet(name, photo_urls, category, tags)
    
    async def get_store_summary(self) -> Dict[str, Any]:
        """Get a summary of store inventory and status
        
        Returns:
            Store summary with inventory counts
        """
        inventory = await self.get_inventory()
        available_pets = await self.find_pets_by_status("available")
        pending_pets = await self.find_pets_by_status("pending")
        sold_pets = await self.find_pets_by_status("sold")
        
        return {
            "inventory": inventory,
            "available_count": len(available_pets) if isinstance(available_pets, list) else 0,
            "pending_count": len(pending_pets) if isinstance(pending_pets, list) else 0,
            "sold_count": len(sold_pets) if isinstance(sold_pets, list) else 0
        }


# Agent-friendly wrapper class
class PetstoreAgent:
    """Agent-friendly wrapper for Petstore operations"""
    
    def __init__(self, server_path: str = "./petstore-mcp-server.py"):
        self.client = PetstoreClient(server_path)
    
    async def execute_pet_workflow(self, workflow_type: str, **kwargs) -> Dict[str, Any]:
        """Execute common pet management workflows
        
        Args:
            workflow_type: Type of workflow (create_pet, find_pets, manage_inventory)
            **kwargs: Workflow-specific parameters
        
        Returns:
            Workflow results
        """
        async with self.client.connect():
            if workflow_type == "create_pet":
                return await self._create_pet_workflow(**kwargs)
            elif workflow_type == "find_pets":
                return await self._find_pets_workflow(**kwargs)
            elif workflow_type == "manage_inventory":
                return await self._manage_inventory_workflow(**kwargs)
            elif workflow_type == "user_management":
                return await self._user_management_workflow(**kwargs)
            else:
                raise ValueError(f"Unknown workflow type: {workflow_type}")
    
    async def _create_pet_workflow(self, name: str, category: str, 
                                  tags: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Workflow for creating a pet with full setup"""
        photo_urls = kwargs.get("photo_urls", [f"https://example.com/{name.lower()}.jpg"])
        
        # Create the pet
        result = await self.client.create_pet_with_category(name, photo_urls, category, tags)
        
        # Get the created pet's ID and fetch full details
        if "id" in result:
            pet_details = await self.client.get_pet_by_id(result["id"])
            return {"created_pet": result, "pet_details": pet_details}
        
        return {"created_pet": result}
    
    async def _find_pets_workflow(self, criteria: str, value: Any, **kwargs) -> Dict[str, Any]:
        """Workflow for finding pets by various criteria"""
        results = {}
        
        if criteria == "status":
            results["pets"] = await self.client.find_pets_by_status(value)
        elif criteria == "tags":
            results["pets"] = await self.client.find_pets_by_tags(value if isinstance(value, list) else [value])
        elif criteria == "id":
            results["pet"] = await self.client.get_pet_by_id(value)
        
        return results
    
    async def _manage_inventory_workflow(self, **kwargs) -> Dict[str, Any]:
        """Workflow for inventory management"""
        return await self.client.get_store_summary()
    
    async def _user_management_workflow(self, action: str, **kwargs) -> Dict[str, Any]:
        """Workflow for user management operations"""
        if action == "create":
            return await self.client.create_user(**kwargs)
        elif action == "login":
            return await self.client.login_user(kwargs["username"], kwargs["password"])
        elif action == "get":
            return await self.client.get_user_by_name(kwargs["username"])
        elif action == "update":
            return await self.client.update_user(kwargs["username"], kwargs["user_data"])
        elif action == "delete":
            return await self.client.delete_user(kwargs["username"])
        else:
            raise ValueError(f"Unknown user action: {action}")


# Example usage and testing
async def main():
    """Example usage of the Petstore client"""
    client = PetstoreClient()
    
    async with client.connect():
        print("Connected to Petstore MCP server!")
        
        # Test inventory
        print("\n=== Getting Inventory ===")
        inventory = await client.get_inventory()
        print(f"Inventory: {inventory}")
        
        # Test finding pets
        print("\n=== Finding Available Pets ===")
        pets = await client.find_pets_by_status("available")
        print(f"Available pets: {pets}")
        
        # Test agent workflow
        print("\n=== Testing Agent Workflow ===")
        agent = PetstoreAgent()
        workflow_result = await agent.execute_pet_workflow(
            "manage_inventory"
        )
        print(f"Inventory workflow result: {workflow_result}")


if __name__ == "__main__":
    asyncio.run(main())
