#!/usr/bin/env python3
"""
Petstore MCP Server

An MCP server that provides tools for interacting with the Swagger Petstore API.
This server implements all the endpoints defined in the OpenAPI specification.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("petstore-mcp-server")

# Base URL for the Petstore API
BASE_URL = "https://petstore3.swagger.io/api/v3"

# Initialize the MCP server
server = Server("petstore-mcp-server")

# HTTP client for making API requests
http_client = httpx.AsyncClient(timeout=30.0)


class PetstoreAPIError(Exception):
    """Custom exception for Petstore API errors"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


async def make_api_request(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    files: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Make an HTTP request to the Petstore API"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        response = await http_client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
            files=files
        )
        
        if response.status_code >= 400:
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                if isinstance(error_data, dict) and "message" in error_data:
                    error_msg = error_data["message"]
            except:
                error_msg = response.text or error_msg
            
            raise PetstoreAPIError(response.status_code, error_msg)
        
        # Handle empty responses
        if not response.content:
            return {"status": "success", "message": "Operation completed successfully"}
        
        try:
            return response.json()
        except:
            return {"status": "success", "data": response.text}
            
    except httpx.RequestError as e:
        raise PetstoreAPIError(0, f"Request failed: {str(e)}")


# Pet Management Tools

@server.call_tool()
async def add_pet(arguments: dict) -> CallToolResult:
    """Add a new pet to the store"""
    try:
        pet_data = arguments.get("pet")
        if not pet_data:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Pet data is required")]
            )
        
        result = await make_api_request("POST", "/pet", json_data=pet_data)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pet added successfully: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error adding pet: {e.message}")]
        )


@server.call_tool()
async def update_pet(arguments: dict) -> CallToolResult:
    """Update an existing pet"""
    try:
        pet_data = arguments.get("pet")
        if not pet_data:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Pet data is required")]
            )
        
        result = await make_api_request("PUT", "/pet", json_data=pet_data)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pet updated successfully: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error updating pet: {e.message}")]
        )


@server.call_tool()
async def get_pet_by_id(arguments: dict) -> CallToolResult:
    """Find pet by ID"""
    try:
        pet_id = arguments.get("pet_id")
        if not pet_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Pet ID is required")]
            )
        
        result = await make_api_request("GET", f"/pet/{pet_id}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pet details: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting pet: {e.message}")]
        )


@server.call_tool()
async def find_pets_by_status(arguments: dict) -> CallToolResult:
    """Find pets by status"""
    try:
        status = arguments.get("status", "available")
        params = {"status": status}
        
        result = await make_api_request("GET", "/pet/findByStatus", params=params)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pets found: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error finding pets by status: {e.message}")]
        )


@server.call_tool()
async def find_pets_by_tags(arguments: dict) -> CallToolResult:
    """Find pets by tags"""
    try:
        tags = arguments.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        
        params = {"tags": tags}
        result = await make_api_request("GET", "/pet/findByTags", params=params)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pets found: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error finding pets by tags: {e.message}")]
        )


@server.call_tool()
async def update_pet_with_form(arguments: dict) -> CallToolResult:
    """Update a pet with form data"""
    try:
        pet_id = arguments.get("pet_id")
        if not pet_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Pet ID is required")]
            )
        
        params = {}
        if arguments.get("name"):
            params["name"] = arguments["name"]
        if arguments.get("status"):
            params["status"] = arguments["status"]
        
        result = await make_api_request("POST", f"/pet/{pet_id}", params=params)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pet updated: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error updating pet: {e.message}")]
        )


@server.call_tool()
async def delete_pet(arguments: dict) -> CallToolResult:
    """Delete a pet"""
    try:
        pet_id = arguments.get("pet_id")
        if not pet_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Pet ID is required")]
            )
        
        headers = {}
        if arguments.get("api_key"):
            headers["api_key"] = arguments["api_key"]
        
        result = await make_api_request("DELETE", f"/pet/{pet_id}", headers=headers)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Pet deleted successfully: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting pet: {e.message}")]
        )


@server.call_tool()
async def upload_pet_image(arguments: dict) -> CallToolResult:
    """Upload an image for a pet"""
    try:
        pet_id = arguments.get("pet_id")
        if not pet_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Pet ID is required")]
            )
        
        # Note: This is a simplified implementation
        # In a real scenario, you'd handle file uploads properly
        params = {}
        if arguments.get("additional_metadata"):
            params["additionalMetadata"] = arguments["additional_metadata"]
        
        # For demonstration, we'll just make the request without actual file data
        result = await make_api_request("POST", f"/pet/{pet_id}/uploadImage", params=params)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Image upload response: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error uploading image: {e.message}")]
        )


# Store Management Tools

@server.call_tool()
async def get_inventory(arguments: dict) -> CallToolResult:
    """Get pet inventories by status"""
    try:
        result = await make_api_request("GET", "/store/inventory")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Inventory: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting inventory: {e.message}")]
        )


@server.call_tool()
async def place_order(arguments: dict) -> CallToolResult:
    """Place an order for a pet"""
    try:
        order_data = arguments.get("order")
        if not order_data:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Order data is required")]
            )
        
        result = await make_api_request("POST", "/store/order", json_data=order_data)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Order placed: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error placing order: {e.message}")]
        )


@server.call_tool()
async def get_order_by_id(arguments: dict) -> CallToolResult:
    """Find purchase order by ID"""
    try:
        order_id = arguments.get("order_id")
        if not order_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Order ID is required")]
            )
        
        result = await make_api_request("GET", f"/store/order/{order_id}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Order details: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting order: {e.message}")]
        )


@server.call_tool()
async def delete_order(arguments: dict) -> CallToolResult:
    """Delete purchase order by ID"""
    try:
        order_id = arguments.get("order_id")
        if not order_id:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Order ID is required")]
            )
        
        result = await make_api_request("DELETE", f"/store/order/{order_id}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Order deleted: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting order: {e.message}")]
        )


# User Management Tools

@server.call_tool()
async def create_user(arguments: dict) -> CallToolResult:
    """Create user"""
    try:
        user_data = arguments.get("user")
        if not user_data:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User data is required")]
            )
        
        result = await make_api_request("POST", "/user", json_data=user_data)
        return CallToolResult(
            content=[TextContent(type="text", text=f"User created: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error creating user: {e.message}")]
        )


@server.call_tool()
async def create_users_with_list(arguments: dict) -> CallToolResult:
    """Create list of users with given input array"""
    try:
        users_data = arguments.get("users")
        if not users_data:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Users data is required")]
            )
        
        result = await make_api_request("POST", "/user/createWithList", json_data=users_data)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Users created: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error creating users: {e.message}")]
        )


@server.call_tool()
async def login_user(arguments: dict) -> CallToolResult:
    """Log user into the system"""
    try:
        params = {}
        if arguments.get("username"):
            params["username"] = arguments["username"]
        if arguments.get("password"):
            params["password"] = arguments["password"]
        
        result = await make_api_request("GET", "/user/login", params=params)
        return CallToolResult(
            content=[TextContent(type="text", text=f"Login successful: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error logging in: {e.message}")]
        )


@server.call_tool()
async def logout_user(arguments: dict) -> CallToolResult:
    """Log out current logged in user session"""
    try:
        result = await make_api_request("GET", "/user/logout")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Logout successful: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error logging out: {e.message}")]
        )


@server.call_tool()
async def get_user_by_name(arguments: dict) -> CallToolResult:
    """Get user by user name"""
    try:
        username = arguments.get("username")
        if not username:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Username is required")]
            )
        
        result = await make_api_request("GET", f"/user/{username}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"User details: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting user: {e.message}")]
        )


@server.call_tool()
async def update_user(arguments: dict) -> CallToolResult:
    """Update user"""
    try:
        username = arguments.get("username")
        user_data = arguments.get("user")
        
        if not username:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Username is required")]
            )
        if not user_data:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: User data is required")]
            )
        
        result = await make_api_request("PUT", f"/user/{username}", json_data=user_data)
        return CallToolResult(
            content=[TextContent(type="text", text=f"User updated: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error updating user: {e.message}")]
        )


@server.call_tool()
async def delete_user(arguments: dict) -> CallToolResult:
    """Delete user"""
    try:
        username = arguments.get("username")
        if not username:
            return CallToolResult(
                content=[TextContent(type="text", text="Error: Username is required")]
            )
        
        result = await make_api_request("DELETE", f"/user/{username}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"User deleted: {json.dumps(result, indent=2)}")]
        )
    except PetstoreAPIError as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting user: {e.message}")]
        )


# Tool definitions for MCP
@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        # Pet Management Tools
        Tool(
            name="add_pet",
            description="Add a new pet to the store",
            inputSchema={
                "type": "object",
                "properties": {
                    "pet": {
                        "type": "object",
                        "description": "Pet object with name, photoUrls, and optional category, tags, status",
                        "required": ["name", "photoUrls"],
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "category": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"}
                                }
                            },
                            "photoUrls": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"}
                                    }
                                }
                            },
                            "status": {
                                "type": "string",
                                "enum": ["available", "pending", "sold"]
                            }
                        }
                    }
                },
                "required": ["pet"]
            }
        ),
        Tool(
            name="update_pet",
            description="Update an existing pet",
            inputSchema={
                "type": "object",
                "properties": {
                    "pet": {
                        "type": "object",
                        "description": "Pet object with updated information",
                        "required": ["name", "photoUrls"],
                        "properties": {
                            "id": {"type": "integer"},
                            "name": {"type": "string"},
                            "category": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "integer"},
                                    "name": {"type": "string"}
                                }
                            },
                            "photoUrls": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "tags": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"}
                                    }
                                }
                            },
                            "status": {
                                "type": "string",
                                "enum": ["available", "pending", "sold"]
                            }
                        }
                    }
                },
                "required": ["pet"]
            }
        ),
        Tool(
            name="get_pet_by_id",
            description="Find pet by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "pet_id": {
                        "type": "integer",
                        "description": "ID of pet to return"
                    }
                },
                "required": ["pet_id"]
            }
        ),
        Tool(
            name="find_pets_by_status",
            description="Find pets by status",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "Status values to filter by",
                        "enum": ["available", "pending", "sold"],
                        "default": "available"
                    }
                }
            }
        ),
        Tool(
            name="find_pets_by_tags",
            description="Find pets by tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Tags to filter by"
                    }
                }
            }
        ),
        Tool(
            name="update_pet_with_form",
            description="Update a pet in the store with form data",
            inputSchema={
                "type": "object",
                "properties": {
                    "pet_id": {
                        "type": "integer",
                        "description": "ID of pet that needs to be updated"
                    },
                    "name": {
                        "type": "string",
                        "description": "Updated name of the pet"
                    },
                    "status": {
                        "type": "string",
                        "description": "Updated status of the pet"
                    }
                },
                "required": ["pet_id"]
            }
        ),
        Tool(
            name="delete_pet",
            description="Delete a pet",
            inputSchema={
                "type": "object",
                "properties": {
                    "pet_id": {
                        "type": "integer",
                        "description": "Pet id to delete"
                    },
                    "api_key": {
                        "type": "string",
                        "description": "API key for authentication"
                    }
                },
                "required": ["pet_id"]
            }
        ),
        Tool(
            name="upload_pet_image",
            description="Upload an image for a pet",
            inputSchema={
                "type": "object",
                "properties": {
                    "pet_id": {
                        "type": "integer",
                        "description": "ID of pet to update"
                    },
                    "additional_metadata": {
                        "type": "string",
                        "description": "Additional metadata"
                    }
                },
                "required": ["pet_id"]
            }
        ),
        
        # Store Management Tools
        Tool(
            name="get_inventory",
            description="Returns pet inventories by status",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="place_order",
            description="Place an order for a pet",
            inputSchema={
                "type": "object",
                "properties": {
                    "order": {
                        "type": "object",
                        "description": "Order object",
                        "properties": {
                            "id": {"type": "integer"},
                            "petId": {"type": "integer"},
                            "quantity": {"type": "integer"},
                            "shipDate": {"type": "string", "format": "date-time"},
                            "status": {
                                "type": "string",
                                "enum": ["placed", "approved", "delivered"]
                            },
                            "complete": {"type": "boolean"}
                        }
                    }
                },
                "required": ["order"]
            }
        ),
        Tool(
            name="get_order_by_id",
            description="Find purchase order by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "ID of order that needs to be fetched"
                    }
                },
                "required": ["order_id"]
            }
        ),
        Tool(
            name="delete_order",
            description="Delete purchase order by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "integer",
                        "description": "ID of the order that needs to be deleted"
                    }
                },
                "required": ["order_id"]
            }
        ),
        
        # User Management Tools
        Tool(
            name="create_user",
            description="Create user",
            inputSchema={
                "type": "object",
                "properties": {
                    "user": {
                        "type": "object",
                        "description": "Created user object",
                        "properties": {
                            "id": {"type": "integer"},
                            "username": {"type": "string"},
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                            "email": {"type": "string"},
                            "password": {"type": "string"},
                            "phone": {"type": "string"},
                            "userStatus": {"type": "integer"}
                        }
                    }
                },
                "required": ["user"]
            }
        ),
        Tool(
            name="create_users_with_list",
            description="Create list of users with given input array",
            inputSchema={
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "integer"},
                                "username": {"type": "string"},
                                "firstName": {"type": "string"},
                                "lastName": {"type": "string"},
                                "email": {"type": "string"},
                                "password": {"type": "string"},
                                "phone": {"type": "string"},
                                "userStatus": {"type": "integer"}
                            }
                        }
                    }
                },
                "required": ["users"]
            }
        ),
        Tool(
            name="login_user",
            description="Log user into the system",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The user name for login"
                    },
                    "password": {
                        "type": "string",
                        "description": "The password for login in clear text"
                    }
                }
            }
        ),
        Tool(
            name="logout_user",
            description="Log out current logged in user session",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_user_by_name",
            description="Get user by user name",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The name that needs to be fetched"
                    }
                },
                "required": ["username"]
            }
        ),
        Tool(
            name="update_user",
            description="Update user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Name that needs to be updated"
                    },
                    "user": {
                        "type": "object",
                        "description": "Updated user object",
                        "properties": {
                            "id": {"type": "integer"},
                            "username": {"type": "string"},
                            "firstName": {"type": "string"},
                            "lastName": {"type": "string"},
                            "email": {"type": "string"},
                            "password": {"type": "string"},
                            "phone": {"type": "string"},
                            "userStatus": {"type": "integer"}
                        }
                    }
                },
                "required": ["username", "user"]
            }
        ),
        Tool(
            name="delete_user",
            description="Delete user",
            inputSchema={
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "The name that needs to be deleted"
                    }
                },
                "required": ["username"]
            }
        )
    ]


async def main():
    """Main function to run the MCP server"""
    # Import here to avoid issues with event loop
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="petstore-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
