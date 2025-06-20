#!/bin/bash

# Setup script for Petstore MCP Server

echo "Setting up Petstore MCP Server..."

# Make the server executable
chmod +x petstore-mcp-server.py

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo "Setup complete!"
echo ""
echo "To use this MCP server with Amazon Q CLI:"
echo "1. Add the server configuration to your MCP settings"
echo "2. The server provides tools for:"
echo "   - Pet management (add, update, find, delete pets)"
echo "   - Store operations (inventory, orders)"
echo "   - User management (create, update, delete users)"
echo ""
echo "Example usage:"
echo "  q chat --mcp-server petstore"
