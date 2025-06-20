# Petstore MCP Server & Client

A comprehensive Model Context Protocol (MCP) implementation for the Swagger Petstore API. This project includes both a complete MCP server and a sophisticated client system for seamless agent integration.

## Overview

This project provides:
- **MCP Server**: Complete implementation of all Petstore API endpoints
- **MCP Client**: High-level client with agent-friendly interfaces
- **Agent Integration**: Ready-to-use components for AI agents
- **Configuration Management**: Flexible configuration system
- **Prompt Templates**: Pre-built prompts for different scenarios

## Project Structure

```
petstore/
├── openapi.yaml              # OpenAPI 3.0 specification
├── petstore-mcp-server.py    # MCP server implementation
├── petstore_mcp_client.py    # Comprehensive MCP client
├── agent_interface.py        # High-level agent interface
├── transport.py              # MCP transport layer
├── prompt_manager.py         # Prompt template management
├── sampling.py               # AI model sampling configurations
├── client_config.py          # Configuration management
├── requirements.txt          # Server dependencies
├── client_requirements.txt   # Client dependencies
├── mcp-server-config.json    # MCP server configuration
├── example_usage.py          # Usage examples
├── test_server.py            # Server testing script
├── setup.sh                  # Setup script
└── README.md                 # This documentation
```

---

# MCP Server

## Features

The MCP server provides comprehensive access to the Petstore API with 19 tools across three categories:

### Pet Management (8 tools)
- **add_pet**: Add a new pet to the store
- **update_pet**: Update an existing pet
- **get_pet_by_id**: Find pet by ID
- **find_pets_by_status**: Find pets by status (available, pending, sold)
- **find_pets_by_tags**: Find pets by tags
- **update_pet_with_form**: Update a pet using form data
- **delete_pet**: Delete a pet
- **upload_pet_image**: Upload an image for a pet

### Store Operations (4 tools)
- **get_inventory**: Get pet inventories by status
- **place_order**: Place an order for a pet
- **get_order_by_id**: Find purchase order by ID
- **delete_order**: Delete purchase order by ID

### User Management (7 tools)
- **create_user**: Create a new user
- **create_users_with_list**: Create multiple users from a list
- **login_user**: Log user into the system
- **logout_user**: Log out current user session
- **get_user_by_name**: Get user by username
- **update_user**: Update user information
- **delete_user**: Delete a user

## Server Installation

1. **Install server dependencies**:
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Make the server executable**:
   ```bash
   chmod +x petstore-mcp-server.py
   ```

3. **Or run the setup script**:
   ```bash
   bash setup.sh
   ```

## Server Configuration

### For Amazon Q CLI

Add the server to your MCP configuration:

```json
{
  "mcpServers": {
    "petstore": {
      "command": "python3",
      "args": ["petstore-mcp-server.py"],
      "cwd": "/path/to/petstore",
      "env": {}
    }
  }
}
```

### Running the Server

```bash
# Direct execution
python3 petstore-mcp-server.py

# With Amazon Q CLI
q chat --mcp-server petstore
```

## Server API Examples

### Pet Management

**Add a new pet**:
```json
{
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
```

**Find pets by status**:
```json
{
  "status": "available"
}
```

### Store Operations

**Place an order**:
```json
{
  "order": {
    "petId": 123,
    "quantity": 1,
    "shipDate": "2024-12-01T10:00:00Z",
    "status": "placed",
    "complete": false
  }
}
```

### User Management

**Create a user**:
```json
{
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
```

---

# MCP Client

## Client Architecture

The MCP client system consists of multiple layers for maximum flexibility and ease of use:

### Core Components

1. **Transport Layer** (`transport.py`)
   - Handles MCP server communication
   - Connection management with async context managers
   - Error handling and logging

2. **Configuration Management** (`client_config.py`)
   - Centralized configuration system
   - Server connection settings
   - Retry policies and caching options

3. **Prompt Management** (`prompt_manager.py`)
   - Template-based prompt generation
   - Different templates for various operations
   - Extensible prompt system

4. **Sampling Configuration** (`sampling.py`)
   - Multiple AI model sampling presets
   - Configurable parameters for different use cases
   - Easy configuration management

5. **Agent Interface** (`agent_interface.py`)
   - High-level task execution
   - Seamless integration of all components
   - Agent-friendly API

## Client Installation

1. **Install client dependencies**:
   ```bash
   pip3 install -r client_requirements.txt
   ```

2. **Ensure server is available**:
   ```bash
   # Make sure the MCP server is in the same directory
   ls petstore-mcp-server.py
   ```

## Client Usage

### Basic Client Usage

```python
from petstore_mcp_client import PetstoreClient

async def main():
    client = PetstoreClient()
    
    async with client.connect():
        # Find available pets
        pets = await client.find_pets_by_status("available")
        
        # Add a new pet
        new_pet = await client.add_pet(
            name="Buddy",
            photo_urls=["https://example.com/buddy.jpg"],
            status="available"
        )
        
        # Get inventory
        inventory = await client.get_inventory()
```

### Agent Interface Usage

```python
from agent_interface import PetstoreAgent
from client_config import ClientConfig

async def main():
    # Initialize agent with configuration
    config = ClientConfig.default()
    agent = PetstoreAgent(config)
    
    # Execute high-level tasks
    result = await agent.execute_task("find_pets", status="available")
    
    # Get prompts for AI models
    prompt = agent.get_prompt("pet_search", status="available", tags=["friendly"])
    
    # Get sampling configuration
    sampling_config = agent.get_sampling_config("balanced")
```

### Advanced Client Features

```python
from petstore_mcp_client import PetstoreAgent

async def main():
    agent = PetstoreAgent()
    
    # Execute complex workflows
    workflow_result = await agent.execute_pet_workflow(
        "create_pet",
        name="Max",
        category="Dogs",
        tags=["friendly", "large"]
    )
    
    # Get store summary
    summary = await agent.client.get_store_summary()
```

## Configuration Options

### Client Configuration

```python
from client_config import ClientConfig, ServerConfig

# Custom configuration
config = ClientConfig(
    server=ServerConfig(
        command="python3",
        args=["./petstore-mcp-server.py"],
        timeout=30
    ),
    retry_attempts=3,
    retry_delay=1.0,
    log_level="INFO",
    enable_caching=True,
    cache_ttl=300
)
```

### Sampling Configurations

Available sampling presets:
- **conservative**: Low temperature, focused responses
- **balanced**: Moderate creativity and focus (default)
- **creative**: Higher temperature, more creative responses
- **precise**: Zero temperature, deterministic responses

```python
from sampling import SamplingManager

sampling = SamplingManager()

# Get different configurations
conservative = sampling.get_config_dict("conservative")
creative = sampling.get_config_dict("creative")
```

### Prompt Templates

Available prompt templates:
- **pet_search**: For finding and filtering pets
- **pet_management**: For pet inventory operations
- **order_processing**: For handling customer orders
- **user_management**: For user account operations

```python
from prompt_manager import PromptManager

prompts = PromptManager()

# Get prompt for pet search
prompt = prompts.get_prompt(
    "pet_search",
    status="available",
    tags=["friendly", "small"]
)
```

## Agent Integration

### Task-Based Operations

The agent interface provides high-level tasks that AI agents can easily use:

```python
# Find pets
await agent.execute_task("find_pets", status="available", tags=["friendly"])

# Manage pets
await agent.execute_task("manage_pet", action="add", name="Buddy", photoUrls=["url"])

# Process orders
await agent.execute_task("process_order", action="place", petId=123, quantity=1)

# Manage users
await agent.execute_task("manage_user", action="create", username="john", email="john@example.com")
```

### Workflow Execution

```python
# Pet management workflow
result = await agent.execute_pet_workflow(
    "create_pet",
    name="Luna",
    category="Cats",
    tags=["indoor", "quiet"],
    photo_urls=["https://example.com/luna.jpg"]
)

# Inventory management workflow
inventory = await agent.execute_pet_workflow("manage_inventory")
```

## Error Handling

The client system includes comprehensive error handling:

- **Network Errors**: Automatic retry with exponential backoff
- **API Errors**: Meaningful error messages and suggestions
- **Validation Errors**: Input validation with helpful feedback
- **Connection Errors**: Graceful degradation and recovery

## Testing

### Server Testing

```bash
# Test server functionality
python3 test_server.py
```

### Client Testing

```bash
# Test client functionality
python3 example_usage.py
```

## API Reference

### Base URL
- Production: `https://petstore3.swagger.io/api/v3`

### Authentication
- API Key authentication for certain endpoints
- OAuth2 support for pet operations

### Rate Limiting
- Configurable retry policies
- Exponential backoff for failed requests

## Development

### Extending the Server

1. Add new tool functions using `@server.call_tool()` decorator
2. Update tool definitions in `handle_list_tools()`
3. Add appropriate error handling and validation
4. Update documentation

### Extending the Client

1. Add new methods to `PetstoreClient` class
2. Create corresponding agent workflows
3. Add prompt templates for new operations
4. Update configuration options

### Adding New Prompts

```python
from prompt_manager import PromptTemplate

# Create new template
template = PromptTemplate(
    system="You are a pet care specialist.",
    user_template="Provide care advice for {pet_type} with {condition}",
    examples={"basic": "Care for a sick dog"}
)

# Add to manager
prompt_manager.add_template("pet_care", template)
```

## Security Considerations

- API keys are handled securely
- Passwords are not logged or cached
- HTTPS connections for all API calls
- Input validation and sanitization
- Error messages don't expose sensitive information

## Performance

- Async/await throughout for non-blocking operations
- Connection pooling for HTTP requests
- Configurable caching with TTL
- Efficient JSON parsing and serialization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## License

This project follows the same license as the Swagger Petstore API (Apache 2.0).

## Support

For issues and questions:
1. Check the example usage scripts
2. Review the test files
3. Examine the configuration options
4. Create an issue with detailed information
