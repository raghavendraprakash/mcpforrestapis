#!/usr/bin/env python3
"""
Agent interface for seamless Petstore MCP integration
"""

import asyncio
import json
from typing import Dict, Any, List, Optional

from transport import MCPTransport
from prompt_manager import PromptManager
from sampling import SamplingManager
from client_config import ClientConfig


class PetstoreAgent:
    """High-level agent interface for Petstore operations"""
    
    def __init__(self, config: Optional[ClientConfig] = None):
        self.config = config or ClientConfig.default()
        self.transport = MCPTransport(self.config.server.args[0])
        self.prompt_manager = PromptManager()
        self.sampling_manager = SamplingManager()
    
    async def execute_task(self, task_type: str, **kwargs) -> Dict[str, Any]:
        """Execute a high-level task"""
        async with self.transport.connect():
            if task_type == "find_pets":
                return await self._find_pets_task(**kwargs)
            elif task_type == "manage_pet":
                return await self._manage_pet_task(**kwargs)
            elif task_type == "process_order":
                return await self._process_order_task(**kwargs)
            elif task_type == "manage_user":
                return await self._manage_user_task(**kwargs)
            else:
                raise ValueError(f"Unknown task type: {task_type}")
    
    async def _find_pets_task(self, status: str = "available", 
                             tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Find pets task"""
        if tags:
            result = await self.transport.call_tool("find_pets_by_tags", {"tags": tags})
        else:
            result = await self.transport.call_tool("find_pets_by_status", {"status": status})
        
        return {"task": "find_pets", "result": result}
    
    async def _manage_pet_task(self, action: str, **pet_data) -> Dict[str, Any]:
        """Manage pet task"""
        if action == "add":
            result = await self.transport.call_tool("add_pet", {"pet": pet_data})
        elif action == "update":
            result = await self.transport.call_tool("update_pet", {"pet": pet_data})
        elif action == "delete":
            result = await self.transport.call_tool("delete_pet", {"pet_id": pet_data["id"]})
        else:
            raise ValueError(f"Unknown pet action: {action}")
        
        return {"task": "manage_pet", "action": action, "result": result}
    
    async def _process_order_task(self, action: str, **order_data) -> Dict[str, Any]:
        """Process order task"""
        if action == "place":
            result = await self.transport.call_tool("place_order", {"order": order_data})
        elif action == "get":
            result = await self.transport.call_tool("get_order_by_id", {"order_id": order_data["id"]})
        elif action == "cancel":
            result = await self.transport.call_tool("delete_order", {"order_id": order_data["id"]})
        else:
            raise ValueError(f"Unknown order action: {action}")
        
        return {"task": "process_order", "action": action, "result": result}
    
    async def _manage_user_task(self, action: str, **user_data) -> Dict[str, Any]:
        """Manage user task"""
        if action == "create":
            result = await self.transport.call_tool("create_user", {"user": user_data})
        elif action == "login":
            result = await self.transport.call_tool("login_user", user_data)
        elif action == "get":
            result = await self.transport.call_tool("get_user_by_name", {"username": user_data["username"]})
        else:
            raise ValueError(f"Unknown user action: {action}")
        
        return {"task": "manage_user", "action": action, "result": result}
    
    def get_prompt(self, task_type: str, **kwargs) -> Dict[str, str]:
        """Get prompt for task type"""
        return self.prompt_manager.get_prompt(task_type, **kwargs)
    
    def get_sampling_config(self, config_name: str = "balanced") -> Dict[str, Any]:
        """Get sampling configuration"""
        return self.sampling_manager.get_config_dict(config_name)
