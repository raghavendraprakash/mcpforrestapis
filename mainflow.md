# Petstore MCP System - Main Functional Flow

This document outlines the complete functional flow of the Petstore MCP Server & Client system, including data structures, API calls, and integration patterns.

## System Architecture Overview

```
AI Agent/Q CLI → Agent Interface → MCP Client → Transport Layer → MCP Server → Petstore API
```

## Core Components Flow

### 1. Initialization Flow

#### Agent Interface Initialization
```python
# Data Flow: Configuration → Agent → Client → Transport
config = ClientConfig.default()
agent = PetstoreAgent(config)
```

**Data Structure:**
```json
{
  "server": {
    "command": "python3",
    "args": ["./petstore-mcp-server.py"],
    "timeout": 30
  },
  "retry_attempts": 3,
  "retry_delay": 1.0,
  "log_level": "INFO",
  "enable_caching": true,
  "cache_ttl": 300
}
```

#### MCP Server Connection
```python
# Transport establishes connection to MCP server
async with client.connect():
    # Server capabilities exchange
    capabilities = await transport.initialize()
```

**Server Capabilities Response:**
```json
{
  "capabilities": {
    "tools": {
      "listChanged": true
    }
  },
  "serverInfo": {
    "name": "petstore-mcp-server",
    "version": "1.0.0"
  }
}
```

### 2. Tool Discovery Flow

#### List Available Tools
```python
tools = await client.list_tools()
```

**Tools Response Data:**
```json
{
  "tools": [
    {
      "name": "add_pet",
      "description": "Add a new pet to the store",
      "inputSchema": {
        "type": "object",
        "properties": {
          "pet": {
            "type": "object",
            "properties": {
              "name": {"type": "string"},
              "photoUrls": {"type": "array", "items": {"type": "string"}},
              "category": {"type": "object"},
              "tags": {"type": "array"},
              "status": {"type": "string", "enum": ["available", "pending", "sold"]}
            },
            "required": ["name", "photoUrls"]
          }
        }
      }
    }
  ]
}
```

## Pet Management Flow

### 3. Add Pet Flow

#### High-Level Agent Call
```python
result = await agent.execute_task("manage_pet", 
    action="add", 
    name="Buddy", 
    photoUrls=["https://example.com/buddy.jpg"],
    category="Dogs",
    tags=["friendly"],
    status="available"
)
```

#### Client Method Call
```python
new_pet = await client.add_pet(
    name="Buddy",
    photo_urls=["https://example.com/buddy.jpg"],
    category={"id": 1, "name": "Dogs"},
    tags=[{"id": 1, "name": "friendly"}],
    status="available"
)
```

#### MCP Tool Call Data
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_pet",
    "arguments": {
      "pet": {
        "name": "Buddy",
        "photoUrls": ["https://example.com/buddy.jpg"],
        "category": {
          "id": 1,
          "name": "Dogs"
        },
        "tags": [
          {
            "id": 1,
            "name": "friendly"
          }
        ],
        "status": "available"
      }
    }
  }
}
```

#### Petstore API Call
```http
POST https://petstore3.swagger.io/api/v3/pet
Content-Type: application/json

{
  "name": "Buddy",
  "photoUrls": ["https://example.com/buddy.jpg"],
  "category": {
    "id": 1,
    "name": "Dogs"
  },
  "tags": [
    {
      "id": 1,
      "name": "friendly"
    }
  ],
  "status": "available"
}
```

#### Response Flow
```json
{
  "content": [
    {
      "type": "text",
      "text": "Pet added successfully with ID: 12345"
    }
  ],
  "isError": false
}
```

### 4. Find Pets Flow

#### Agent Task Execution
```python
pets = await agent.execute_task("find_pets", 
    status="available", 
    tags=["friendly"]
)
```

#### Client Method with Filtering
```python
# Find by status
available_pets = await client.find_pets_by_status("available")

# Find by tags
tagged_pets = await client.find_pets_by_tags(["friendly", "small"])
```

#### MCP Tool Call for Status Search
```json
{
  "method": "tools/call",
  "params": {
    "name": "find_pets_by_status",
    "arguments": {
      "status": "available"
    }
  }
}
```

#### Petstore API Call
```http
GET https://petstore3.swagger.io/api/v3/pet/findByStatus?status=available
```

#### Response Data Structure
```json
{
  "content": [
    {
      "type": "text",
      "text": "Found 5 pets with status 'available':\n- Buddy (ID: 12345, Tags: friendly)\n- Luna (ID: 12346, Tags: quiet, indoor)\n..."
    }
  ],
  "pets": [
    {
      "id": 12345,
      "name": "Buddy",
      "category": {"id": 1, "name": "Dogs"},
      "photoUrls": ["https://example.com/buddy.jpg"],
      "tags": [{"id": 1, "name": "friendly"}],
      "status": "available"
    }
  ]
}
```

## Store Operations Flow

### 5. Place Order Flow

#### Agent Workflow
```python
order_result = await agent.execute_task("process_order",
    action="place",
    petId=12345,
    quantity=1,
    shipDate="2024-12-01T10:00:00Z"
)
```

#### Client Order Placement
```python
order = await client.place_order(
    pet_id=12345,
    quantity=1,
    ship_date="2024-12-01T10:00:00Z",
    status="placed"
)
```

#### MCP Tool Call Data
```json
{
  "method": "tools/call",
  "params": {
    "name": "place_order",
    "arguments": {
      "order": {
        "petId": 12345,
        "quantity": 1,
        "shipDate": "2024-12-01T10:00:00Z",
        "status": "placed",
        "complete": false
      }
    }
  }
}
```

#### Petstore API Call
```http
POST https://petstore3.swagger.io/api/v3/store/order
Content-Type: application/json

{
  "petId": 12345,
  "quantity": 1,
  "shipDate": "2024-12-01T10:00:00Z",
  "status": "placed",
  "complete": false
}
```

#### Order Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "Order placed successfully with ID: 67890"
    }
  ],
  "order": {
    "id": 67890,
    "petId": 12345,
    "quantity": 1,
    "shipDate": "2024-12-01T10:00:00Z",
    "status": "placed",
    "complete": false
  }
}
```

### 6. Inventory Check Flow

#### Agent Inventory Request
```python
inventory = await agent.execute_task("check_inventory")
```

#### Client Inventory Call
```python
inventory = await client.get_inventory()
```

#### MCP Tool Call
```json
{
  "method": "tools/call",
  "params": {
    "name": "get_inventory",
    "arguments": {}
  }
}
```

#### Petstore API Call
```http
GET https://petstore3.swagger.io/api/v3/store/inventory
```

#### Inventory Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "Current inventory status:\n- available: 15\n- pending: 3\n- sold: 7"
    }
  ],
  "inventory": {
    "available": 15,
    "pending": 3,
    "sold": 7
  }
}
```

## User Management Flow

### 7. Create User Flow

#### Agent User Creation
```python
user_result = await agent.execute_task("manage_user",
    action="create",
    username="johndoe",
    email="john@example.com",
    firstName="John",
    lastName="Doe"
)
```

#### Client User Creation
```python
user = await client.create_user(
    username="johndoe",
    first_name="John",
    last_name="Doe",
    email="john@example.com",
    password="password123",
    phone="555-1234"
)
```

#### MCP Tool Call Data
```json
{
  "method": "tools/call",
  "params": {
    "name": "create_user",
    "arguments": {
      "user": {
        "username": "johndoe",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john@example.com",
        "password": "password123",
        "phone": "555-1234",
        "userStatus": 1
      }
    }
  }
}
```

#### Petstore API Call
```http
POST https://petstore3.swagger.io/api/v3/user
Content-Type: application/json

{
  "username": "johndoe",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john@example.com",
  "password": "password123",
  "phone": "555-1234",
  "userStatus": 1
}
```

## Prompt Integration Flow

### 8. AI Model Integration

#### Prompt Generation
```python
prompt = agent.get_prompt("pet_search", 
    status="available", 
    tags=["friendly", "small"]
)
```

#### Prompt Template Data
```json
{
  "system": "You are a pet store assistant helping customers find the perfect pet.",
  "user": "Find pets with status: available and tags: friendly, small. Provide detailed information about each pet including care requirements.",
  "examples": {
    "basic": "Search for available pets",
    "filtered": "Find friendly small pets that are available"
  }
}
```

#### Sampling Configuration
```python
sampling_config = agent.get_sampling_config("balanced")
```

#### Sampling Data
```json
{
  "temperature": 0.7,
  "max_tokens": 1000,
  "top_p": 0.9,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
```

## Error Handling Flow

### 9. Error Response Flow

#### Network Error Handling
```python
try:
    result = await client.add_pet(name="Test", photo_urls=["url"])
except ConnectionError as e:
    # Retry with exponential backoff
    await asyncio.sleep(retry_delay)
    result = await client.add_pet(name="Test", photo_urls=["url"])
```

#### API Error Response
```json
{
  "content": [
    {
      "type": "text",
      "text": "Error: Pet validation failed - name is required"
    }
  ],
  "isError": true,
  "error": {
    "code": 400,
    "message": "Invalid input",
    "details": "Pet name cannot be empty"
  }
}
```

#### Validation Error Flow
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_pet",
    "arguments": {
      "pet": {
        "photoUrls": ["url"]
        // Missing required "name" field
      }
    }
  }
}
```

## Complete Workflow Examples

### 10. End-to-End Pet Adoption Workflow

```python
async def pet_adoption_workflow():
    agent = PetstoreAgent()
    
    # 1. Find available pets
    pets = await agent.execute_task("find_pets", status="available")
    
    # 2. Select a pet (ID: 12345)
    pet_details = await agent.execute_task("get_pet", pet_id=12345)
    
    # 3. Create user account
    user = await agent.execute_task("manage_user", 
        action="create",
        username="adopter123",
        email="adopter@example.com"
    )
    
    # 4. Place adoption order
    order = await agent.execute_task("process_order",
        action="place",
        petId=12345,
        quantity=1
    )
    
    # 5. Update pet status to sold
    await agent.execute_task("manage_pet",
        action="update",
        pet_id=12345,
        status="sold"
    )
    
    return {
        "pet": pet_details,
        "user": user,
        "order": order,
        "status": "adoption_complete"
    }
```

### 11. Data Flow Summary

```
Input Data → Agent Interface → Prompt Generation → MCP Client → Transport Layer → MCP Server → Petstore API
                ↓                    ↓                ↓              ↓               ↓            ↓
         Task Execution → AI Integration → Tool Calls → HTTP Requests → API Responses → Formatted Results
```

## Configuration Data Structures

### 12. Complete Configuration Flow

#### Client Configuration
```json
{
  "server": {
    "command": "python3",
    "args": ["./petstore-mcp-server.py"],
    "cwd": "/path/to/petstore",
    "timeout": 30,
    "env": {}
  },
  "transport": {
    "retry_attempts": 3,
    "retry_delay": 1.0,
    "connection_timeout": 10.0
  },
  "caching": {
    "enable_caching": true,
    "cache_ttl": 300,
    "max_cache_size": 1000
  },
  "logging": {
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  }
}
```

#### MCP Server Configuration
```json
{
  "mcpServers": {
    "petstore": {
      "command": "python3",
      "args": ["petstore-mcp-server.py"],
      "cwd": "/Users/rp/RP_HOME/experiments/qcli/mcpforrestapis",
      "env": {
        "PETSTORE_API_URL": "https://petstore3.swagger.io/api/v3",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

This document provides a comprehensive overview of all functional flows, data structures, and integration patterns in the Petstore MCP system. Each section includes the actual data that flows through the system at each step, making it easy to understand and debug the complete workflow.
