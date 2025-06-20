#!/usr/bin/env python3
"""
Transport layer for MCP client communication
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPTransport:
    """Handles MCP server communication"""
    
    def __init__(self, server_path: str = "./petstore-mcp-server.py"):
        self.server_path = server_path
        self.session: Optional[ClientSession] = None
        self._server_params = StdioServerParameters(
            command="python3",
            args=[server_path],
            env=None
        )
    
    @asynccontextmanager
    async def connect(self):
        """Connect to MCP server"""
        try:
            async with stdio_client(self._server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    self.session = session
                    await session.initialize()
                    
                    tools = await session.list_tools()
                    logger.info(f"Connected with {len(tools.tools)} tools")
                    
                    yield self
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool"""
        if not self.session:
            raise RuntimeError("Not connected to server")
        
        try:
            result = await self.session.call_tool(tool_name, arguments)
            
            if result.content and len(result.content) > 0:
                content = result.content[0]
                if hasattr(content, 'text'):
                    return {"response": content.text}
            
            return {"status": "success"}
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
