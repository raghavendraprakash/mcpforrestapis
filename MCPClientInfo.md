# MCP Client Reference Guide

This document provides a comprehensive reference for using the Petstore MCP Client system, explaining all code block functionalities and usage patterns.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Components](#core-components)
3. [Client Configuration](#client-configuration)
4. [Transport Layer](#transport-layer)
5. [Prompt Management](#prompt-management)
6. [Sampling Configuration](#sampling-configuration)
7. [Agent Interface](#agent-interface)
8. [Usage Patterns](#usage-patterns)
9. [Error Handling](#error-handling)
10. [Best Practices](#best-practices)

---

## Architecture Overview

The MCP Client system follows a layered architecture designed for flexibility and ease of use:

```
┌─────────────────────────────────────┐
│           Agent Interface           │  ← High-level API for agents
├─────────────────────────────────────┤
│      Prompt & Sampling Managers    │  ← AI model integration
├─────────────────────────────────────┤
│         Transport Layer             │  ← MCP communication
├─────────────────────────────────────┤
│      Configuration Management       │  ← Settings and policies
└─────────────────────────────────────┘
```

Each layer provides specific functionality while maintaining clean separation of concerns.

---

## Core Components

### 1. PetstoreClient (`petstore_mcp_client.py`)

The main client class that provides direct access to all Petstore API operations.

#### Key Methods:

```python
class PetstoreClient:
    def __init__(self, server_path: str = "./petstore-mcp-server.py")
    
    @asynccontextmanager
    async def connect(self)  # Connection management
    
    # Pet Management
    async def add_pet(self, name, photo_urls, category=None, tags=None, status="available")
    async def update_pet(self, pet_id, name, photo_urls, category=None, tags=None, status="available")
    async def get_pet_by_id(self, pet_id)
    async def find_pets_by_status(self, status="available")
    async def find_pets_by_tags(self, tags)
    async def delete_pet(self, pet_id, api_key=None)
    
    # Store Operations
    async def get_inventory(self)
    async def place_order(self, pet_id, quantity=1, ship_date=None, status="placed", complete=False)
    async def get_order_by_id(self, order_id)
    async def delete_order(self, order_id)
    
    # User Management
    async def create_user(self, username, first_name, last_name, email, password, phone=None, user_status=1)
    async def login_user(self, username, password)
    async def get_user_by_name(self, username)
    async def update_user(self, username, user_data)
    async def delete_user(self, username)
```

#### Usage Example:

```python
from petstore_mcp_client import PetstoreClient

async def example_usage():
    client = PetstoreClient()
    
    async with client.connect():
        # Add a new pet
        result = await client.add_pet(
            name="Buddy",
            photo_urls=["https://example.com/buddy.jpg"],
            category={"id": 1, "name": "Dogs"},
            tags=[{"id": 1, "name": "friendly"}],
            status="available"
        )
        
        # Find available pets
        pets = await client.find_pets_by_status("available")
        
        # Place an order
        order = await client.place_order(
            pet_id=123,
            quantity=1,
            status="placed"
        )
```

### 2. Connection Management

The client uses async context managers for proper resource management:

```python
# Automatic connection handling
async with client.connect():
    # All operations here have an active connection
    result = await client.get_inventory()
    # Connection automatically closed when exiting context
```

**Key Features:**
- Automatic connection establishment and cleanup
- Session initialization and tool discovery
- Error handling for connection failures
- Resource management

---

## Client Configuration

### Configuration Classes (`client_config.py`)

#### ServerConfig

Manages MCP server connection parameters:

```python
@dataclass
class ServerConfig:
    command: str = "python3"                    # Command to run server
    args: List[str] = ["./petstore-mcp-server.py"]  # Server arguments
    cwd: Optional[str] = None                   # Working directory
    env: Optional[Dict[str, str]] = None        # Environment variables
    timeout: int = 30                           # Connection timeout
```

#### ClientConfig

Main configuration for client behavior:

```python
@dataclass
class ClientConfig:
    server: ServerConfig                        # Server connection config
    retry_attempts: int = 3                     # Number of retry attempts
    retry_delay: float = 1.0                    # Delay between retries
    log_level: str = "INFO"                     # Logging level
    enable_caching: bool = True                 # Enable response caching
    cache_ttl: int = 300                        # Cache time-to-live (seconds)
```

#### Usage Examples:

```python
from client_config import ClientConfig, ServerConfig

# Default configuration
config = ClientConfig.default()

# Custom configuration
custom_config = ClientConfig(
    server=ServerConfig(
        command="python3",
        args=["./petstore-mcp-server.py"],
        timeout=60
    ),
    retry_attempts=5,
    retry_delay=2.0,
    log_level="DEBUG"
)

# From dictionary
config_dict = {
    "server": {
        "command": "python3",
        "args": ["./petstore-mcp-server.py"],
        "timeout": 30
    },
    "retry_attempts": 3,
    "log_level": "INFO"
}
config = ClientConfig.from_dict(config_dict)
```

---

## Transport Layer

### MCPTransport (`transport.py`)

Handles low-level MCP communication with the server.

#### Key Methods:

```python
class MCPTransport:
    def __init__(self, server_path: str = "./petstore-mcp-server.py")
    
    @asynccontextmanager
    async def connect(self)  # Establish MCP connection
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]
```

#### Internal Functionality:

```python
# Connection establishment
async with stdio_client(self._server_params) as (read, write):
    async with ClientSession(read, write) as session:
        self.session = session
        await session.initialize()
        
        # Tool discovery
        tools = await session.list_tools()
        logger.info(f"Connected with {len(tools.tools)} tools")
```

#### Error Handling:

```python
try:
    result = await self.session.call_tool(tool_name, arguments)
    # Process result...
except Exception as e:
    logger.error(f"Tool call failed: {e}")
    return {"error": str(e)}
```

**Key Features:**
- Automatic session management
- Tool discovery and validation
- Response parsing and error handling
- Logging and debugging support

---

## Prompt Management

### PromptManager (`prompt_manager.py`)

Manages prompt templates for different AI model interactions.

#### PromptTemplate Structure:

```python
@dataclass
class PromptTemplate:
    system: str                                 # System prompt
    user_template: str                          # User prompt template
    examples: Optional[Dict[str, str]] = None   # Usage examples
```

#### Built-in Templates:

```python
templates = {
    "pet_search": PromptTemplate(
        system="You are a pet store assistant. Help users find pets.",
        user_template="Find pets with status: {status}, tags: {tags}",
        examples={
            "basic": "Find available dogs",
            "advanced": "Find available pets with tags: friendly, small"
        }
    ),
    
    "pet_management": PromptTemplate(
        system="You are a pet store manager. Help manage pet inventory.",
        user_template="Action: {action}, Pet: {pet_details}",
        examples={
            "add": "Add a new dog named Buddy",
            "update": "Update pet status to sold"
        }
    ),
    
    "order_processing": PromptTemplate(
        system="You are an order processor. Handle customer orders.",
        user_template="Process order for pet {pet_id}, quantity: {quantity}",
        examples={
            "simple": "Order 1 pet with ID 123",
            "complex": "Order 2 pets with special delivery"
        }
    )
}
```

#### Usage Examples:

```python
from prompt_manager import PromptManager, PromptTemplate

# Initialize manager
prompt_manager = PromptManager()

# Get existing prompt
prompt = prompt_manager.get_prompt(
    "pet_search",
    status="available",
    tags=["friendly", "small"]
)
# Returns: {
#     "system": "You are a pet store assistant...",
#     "user": "Find pets with status: available, tags: ['friendly', 'small']"
# }

# Add custom template
custom_template = PromptTemplate(
    system="You are a pet care specialist.",
    user_template="Provide care advice for {pet_type} with {condition}",
    examples={"basic": "Care for a sick dog"}
)
prompt_manager.add_template("pet_care", custom_template)

# Use custom template
care_prompt = prompt_manager.get_prompt(
    "pet_care",
    pet_type="dog",
    condition="upset stomach"
)
```

---

## Sampling Configuration

### SamplingManager (`sampling.py`)

Manages AI model sampling parameters for different use cases.

#### SamplingConfig Structure:

```python
@dataclass
class SamplingConfig:
    temperature: float = 0.3                    # Randomness (0.0-1.0)
    top_p: float = 0.9                          # Nucleus sampling
    max_tokens: int = 1500                      # Maximum response length
    frequency_penalty: float = 0.1              # Repetition penalty
    presence_penalty: float = 0.1               # Topic diversity
    stop_sequences: Optional[list] = None       # Stop generation tokens
```

#### Built-in Configurations:

```python
configs = {
    "conservative": SamplingConfig(
        temperature=0.1,        # Very focused responses
        top_p=0.9,
        max_tokens=1000,
        frequency_penalty=0.0,
        presence_penalty=0.0
    ),
    
    "balanced": SamplingConfig(
        temperature=0.3,        # Moderate creativity
        top_p=0.9,
        max_tokens=1500,
        frequency_penalty=0.1,
        presence_penalty=0.1
    ),
    
    "creative": SamplingConfig(
        temperature=0.7,        # High creativity
        top_p=0.95,
        max_tokens=2000,
        frequency_penalty=0.2,
        presence_penalty=0.2
    ),
    
    "precise": SamplingConfig(
        temperature=0.0,        # Deterministic responses
        top_p=1.0,
        max_tokens=800,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
}
```

#### Usage Examples:

```python
from sampling import SamplingManager, SamplingConfig

# Initialize manager
sampling_manager = SamplingManager()

# Get configuration as object
config = sampling_manager.get_config("balanced")
print(f"Temperature: {config.temperature}")

# Get configuration as dictionary (for API calls)
config_dict = sampling_manager.get_config_dict("creative")
# Returns: {
#     "temperature": 0.7,
#     "top_p": 0.95,
#     "max_tokens": 2000,
#     "frequency_penalty": 0.2,
#     "presence_penalty": 0.2,
#     "stop": None
# }

# Add custom configuration
custom_config = SamplingConfig(
    temperature=0.5,
    max_tokens=1200,
    frequency_penalty=0.15
)
sampling_manager.add_config("custom", custom_config)
```

---

## Agent Interface

### PetstoreAgent (`agent_interface.py`)

High-level interface designed for AI agents to easily interact with the Petstore API.

#### Key Methods:

```python
class PetstoreAgent:
    def __init__(self, config: Optional[ClientConfig] = None)
    
    # High-level task execution
    async def execute_task(self, task_type: str, **kwargs) -> Dict[str, Any]
    
    # Prompt and sampling integration
    def get_prompt(self, task_type: str, **kwargs) -> Dict[str, str]
    def get_sampling_config(self, config_name: str = "balanced") -> Dict[str, Any]
```

#### Task Types:

```python
# Available task types
TASK_TYPES = {
    "find_pets": "Search for pets by status or tags",
    "manage_pet": "Add, update, or delete pets",
    "process_order": "Handle customer orders",
    "manage_user": "User account operations"
}
```

#### Usage Examples:

```python
from agent_interface import PetstoreAgent
from client_config import ClientConfig

# Initialize agent
config = ClientConfig.default()
agent = PetstoreAgent(config)

# Execute tasks
result = await agent.execute_task(
    "find_pets",
    status="available",
    tags=["friendly"]
)

result = await agent.execute_task(
    "manage_pet",
    action="add",
    name="Buddy",
    photoUrls=["https://example.com/buddy.jpg"],
    status="available"
)

result = await agent.execute_task(
    "process_order",
    action="place",
    petId=123,
    quantity=1
)

result = await agent.execute_task(
    "manage_user",
    action="create",
    username="john",
    firstName="John",
    lastName="Doe",
    email="john@example.com",
    password="password123"
)

# Get prompts and sampling configs
prompt = agent.get_prompt("pet_search", status="available", tags=["friendly"])
sampling = agent.get_sampling_config("balanced")
```

#### Internal Task Handlers:

```python
async def _find_pets_task(self, status: str = "available", 
                         tags: Optional[List[str]] = None) -> Dict[str, Any]:
    """Find pets task implementation"""
    if tags:
        result = await self.transport.call_tool("find_pets_by_tags", {"tags": tags})
    else:
        result = await self.transport.call_tool("find_pets_by_status", {"status": status})
    
    return {"task": "find_pets", "result": result}

async def _manage_pet_task(self, action: str, **pet_data) -> Dict[str, Any]:
    """Manage pet task implementation"""
    if action == "add":
        result = await self.transport.call_tool("add_pet", {"pet": pet_data})
    elif action == "update":
        result = await self.transport.call_tool("update_pet", {"pet": pet_data})
    elif action == "delete":
        result = await self.transport.call_tool("delete_pet", {"pet_id": pet_data["id"]})
    else:
        raise ValueError(f"Unknown pet action: {action}")
    
    return {"task": "manage_pet", "action": action, "result": result}
```

---

## Usage Patterns

### Pattern 1: Direct Client Usage

For applications that need direct control over API calls:

```python
from petstore_mcp_client import PetstoreClient

async def direct_usage():
    client = PetstoreClient()
    
    async with client.connect():
        # Direct API calls
        pets = await client.find_pets_by_status("available")
        
        # Complex operations
        new_pet = await client.add_pet(
            name="Max",
            photo_urls=["https://example.com/max.jpg"],
            category={"id": 2, "name": "Cats"},
            tags=[{"id": 1, "name": "playful"}]
        )
        
        # Order processing
        order = await client.place_order(
            pet_id=new_pet.get("id"),
            quantity=1,
            status="placed"
        )
```

### Pattern 2: Agent-Based Usage

For AI agents that need high-level task execution:

```python
from agent_interface import PetstoreAgent

async def agent_usage():
    agent = PetstoreAgent()
    
    # Task-based operations
    pets_result = await agent.execute_task("find_pets", status="available")
    
    # Get AI prompts
    prompt = agent.get_prompt("pet_search", status="available", tags=["friendly"])
    
    # Get sampling configuration
    sampling_config = agent.get_sampling_config("balanced")
    
    # Use in AI model call (pseudo-code)
    # response = await ai_model.generate(
    #     system=prompt["system"],
    #     user=prompt["user"],
    #     **sampling_config
    # )
```

### Pattern 3: Configuration-Driven Usage

For applications with specific configuration requirements:

```python
from client_config import ClientConfig, ServerConfig
from agent_interface import PetstoreAgent

async def configured_usage():
    # Custom configuration
    config = ClientConfig(
        server=ServerConfig(
            command="python3",
            args=["./petstore-mcp-server.py"],
            timeout=60
        ),
        retry_attempts=5,
        retry_delay=2.0,
        log_level="DEBUG",
        enable_caching=True,
        cache_ttl=600
    )
    
    # Use with agent
    agent = PetstoreAgent(config)
    
    # Execute tasks with custom configuration
    result = await agent.execute_task("find_pets", status="available")
```

### Pattern 4: Workflow-Based Usage

For complex multi-step operations:

```python
async def workflow_usage():
    agent = PetstoreAgent()
    
    # Multi-step workflow
    async def pet_adoption_workflow(pet_name, adopter_info):
        # Step 1: Find available pets
        pets = await agent.execute_task("find_pets", status="available")
        
        # Step 2: Create user account
        user = await agent.execute_task(
            "manage_user",
            action="create",
            **adopter_info
        )
        
        # Step 3: Place adoption order
        if pets and user:
            order = await agent.execute_task(
                "process_order",
                action="place",
                petId=pets[0]["id"],
                quantity=1
            )
            
            return {"success": True, "order": order}
        
        return {"success": False, "error": "Workflow failed"}
    
    # Execute workflow
    result = await pet_adoption_workflow(
        "Buddy",
        {
            "username": "john_doe",
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "password": "secure_password"
        }
    )
```

---

## Error Handling

### Error Types and Handling Strategies

#### 1. Connection Errors

```python
from transport import MCPTransport

async def handle_connection_errors():
    transport = MCPTransport()
    
    try:
        async with transport.connect():
            result = await transport.call_tool("get_inventory", {})
    except ConnectionError as e:
        print(f"Failed to connect to MCP server: {e}")
        # Implement retry logic or fallback
    except TimeoutError as e:
        print(f"Connection timed out: {e}")
        # Handle timeout scenario
```

#### 2. API Errors

```python
async def handle_api_errors():
    client = PetstoreClient()
    
    async with client.connect():
        try:
            result = await client.get_pet_by_id(999999)  # Non-existent pet
        except Exception as e:
            if "404" in str(e):
                print("Pet not found")
            elif "400" in str(e):
                print("Invalid request")
            else:
                print(f"Unexpected error: {e}")
```

#### 3. Validation Errors

```python
async def handle_validation_errors():
    client = PetstoreClient()
    
    async with client.connect():
        try:
            # Missing required fields
            result = await client.add_pet(
                name="",  # Empty name
                photo_urls=[]  # Empty photo URLs
            )
        except ValueError as e:
            print(f"Validation error: {e}")
            # Handle validation failure
```

#### 4. Retry Logic

```python
import asyncio
from typing import Callable, Any

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    backoff_factor: float = 2.0,
    *args,
    **kwargs
) -> Any:
    """Retry function with exponential backoff"""
    
    for attempt in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = backoff_factor ** attempt
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
            await asyncio.sleep(wait_time)

# Usage
async def resilient_operation():
    client = PetstoreClient()
    
    async with client.connect():
        result = await retry_with_backoff(
            client.get_inventory,
            max_retries=3,
            backoff_factor=2.0
        )
```

---

## Best Practices

### 1. Resource Management

Always use context managers for proper resource cleanup:

```python
# ✅ Good - Automatic cleanup
async with client.connect():
    result = await client.get_inventory()

# ❌ Bad - Manual management required
client = PetstoreClient()
# ... operations without proper cleanup
```

### 2. Error Handling

Implement comprehensive error handling:

```python
# ✅ Good - Specific error handling
try:
    result = await client.get_pet_by_id(pet_id)
except ConnectionError:
    # Handle connection issues
    pass
except ValueError:
    # Handle validation errors
    pass
except Exception as e:
    # Handle unexpected errors
    logger.error(f"Unexpected error: {e}")

# ❌ Bad - Generic error handling
try:
    result = await client.get_pet_by_id(pet_id)
except Exception:
    pass  # Silent failure
```

### 3. Configuration Management

Use configuration objects for maintainable code:

```python
# ✅ Good - Centralized configuration
config = ClientConfig(
    server=ServerConfig(timeout=60),
    retry_attempts=5,
    log_level="DEBUG"
)
agent = PetstoreAgent(config)

# ❌ Bad - Hardcoded values
agent = PetstoreAgent()
# Hardcoded timeouts and retries in code
```

### 4. Logging and Monitoring

Implement proper logging:

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def monitored_operation():
    logger.info("Starting pet search operation")
    
    try:
        result = await agent.execute_task("find_pets", status="available")
        logger.info(f"Found {len(result.get('pets', []))} pets")
        return result
    except Exception as e:
        logger.error(f"Pet search failed: {e}")
        raise
```

### 5. Async Best Practices

Use proper async patterns:

```python
# ✅ Good - Concurrent operations
async def concurrent_operations():
    async with client.connect():
        # Run operations concurrently
        inventory_task = client.get_inventory()
        pets_task = client.find_pets_by_status("available")
        
        inventory, pets = await asyncio.gather(inventory_task, pets_task)
        
        return {"inventory": inventory, "pets": pets}

# ❌ Bad - Sequential operations
async def sequential_operations():
    async with client.connect():
        inventory = await client.get_inventory()
        pets = await client.find_pets_by_status("available")
        
        return {"inventory": inventory, "pets": pets}
```

### 6. Data Validation

Validate input data before API calls:

```python
def validate_pet_data(pet_data: dict) -> bool:
    """Validate pet data before creation"""
    required_fields = ["name", "photoUrls"]
    
    for field in required_fields:
        if not pet_data.get(field):
            raise ValueError(f"Missing required field: {field}")
    
    if not isinstance(pet_data["photoUrls"], list):
        raise ValueError("photoUrls must be a list")
    
    return True

async def create_pet_safely(pet_data: dict):
    validate_pet_data(pet_data)
    
    async with client.connect():
        return await client.add_pet(**pet_data)
```

This reference guide provides comprehensive information about the MCP Client system, enabling developers and AI agents to effectively use all available functionalities.
