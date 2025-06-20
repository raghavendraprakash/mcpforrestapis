#!/usr/bin/env python3
"""
Configuration and settings for the Petstore MCP Client
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import os


@dataclass
class ServerConfig:
    """Configuration for MCP server connection"""
    command: str = "python3"
    args: List[str] = None
    cwd: Optional[str] = None
    env: Optional[Dict[str, str]] = None
    timeout: int = 30
    
    def __post_init__(self):
        if self.args is None:
            self.args = ["./petstore-mcp-server.py"]
        if self.cwd is None:
            self.cwd = os.getcwd()


@dataclass
class ClientConfig:
    """Main client configuration"""
    server: ServerConfig
    retry_attempts: int = 3
    retry_delay: float = 1.0
    log_level: str = "INFO"
    enable_caching: bool = True
    cache_ttl: int = 300  # 5 minutes
    
    @classmethod
    def default(cls) -> 'ClientConfig':
        """Create default configuration"""
        return cls(
            server=ServerConfig(),
            retry_attempts=3,
            retry_delay=1.0,
            log_level="INFO",
            enable_caching=True,
            cache_ttl=300
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ClientConfig':
        """Create configuration from dictionary"""
        server_config = ServerConfig(**config_dict.get("server", {}))
        
        return cls(
            server=server_config,
            retry_attempts=config_dict.get("retry_attempts", 3),
            retry_delay=config_dict.get("retry_delay", 1.0),
            log_level=config_dict.get("log_level", "INFO"),
            enable_caching=config_dict.get("enable_caching", True),
            cache_ttl=config_dict.get("cache_ttl", 300)
        )


# Prompt templates for different operations
PROMPT_TEMPLATES = {
    "pet_search": {
        "system": """You are a pet store assistant. Help users find pets based on their criteria.
Available statuses: available, pending, sold
You can search by status, tags, or specific pet ID.""",
        
        "user_template": """Find pets with the following criteria:
- Status: {status}
- Tags: {tags}
- Additional filters: {filters}

Please provide a summary of matching pets."""
    },
    
    "pet_management": {
        "system": """You are a pet store manager. Help with pet inventory management.
You can add, update, or remove pets from the store inventory.""",
        
        "user_template": """Perform the following pet management task:
- Action: {action}
- Pet details: {pet_details}
- Additional parameters: {parameters}

Ensure all required fields are provided."""
    },
    
    "order_processing": {
        "system": """You are an order processing assistant. Help with customer orders.
You can create orders, check order status, and manage order fulfillment.""",
        
        "user_template": """Process the following order request:
- Customer: {customer}
- Pet ID: {pet_id}
- Quantity: {quantity}
- Special instructions: {instructions}

Verify pet availability before processing."""
    },
    
    "user_management": {
        "system": """You are a user account manager. Help with user registration and account management.
You can create users, update profiles, and manage authentication.""",
        
        "user_template": """Handle the following user management task:
- Action: {action}
- User details: {user_details}
- Authentication: {auth_info}

Ensure data privacy and security requirements are met."""
    }
}

# Sampling configurations for different use cases
SAMPLING_CONFIGS = {
    "conservative": {
        "temperature": 0.1,
        "top_p": 0.9,
        "max_tokens": 1000,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    },
    
    "balanced": {
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 1500,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    },
    
    "creative": {
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 2000,
        "frequency_penalty": 0.2,
        "presence_penalty": 0.2
    }
}

# Tool usage patterns for different scenarios
TOOL_PATTERNS = {
    "pet_discovery": [
        "find_pets_by_status",
        "find_pets_by_tags",
        "get_pet_by_id"
    ],
    
    "pet_lifecycle": [
        "add_pet",
        "update_pet",
        "update_pet_with_form",
        "upload_pet_image",
        "delete_pet"
    ],
    
    "store_operations": [
        "get_inventory",
        "place_order",
        "get_order_by_id",
        "delete_order"
    ],
    
    "user_lifecycle": [
        "create_user",
        "login_user",
        "get_user_by_name",
        "update_user",
        "logout_user",
        "delete_user"
    ]
}

# Error handling strategies
ERROR_STRATEGIES = {
    "retry_on_network": {
        "max_retries": 3,
        "backoff_factor": 2.0,
        "retry_status_codes": [500, 502, 503, 504]
    },
    
    "graceful_degradation": {
        "fallback_responses": True,
        "partial_results": True,
        "error_logging": True
    },
    
    "user_friendly": {
        "translate_errors": True,
        "provide_suggestions": True,
        "include_help_links": True
    }
}
