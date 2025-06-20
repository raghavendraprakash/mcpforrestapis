#!/usr/bin/env python3
"""
Prompt management system for Petstore MCP Client
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Template for generating prompts"""
    system: str
    user_template: str
    examples: Optional[Dict[str, str]] = None


class PromptManager:
    """Manages prompts for different Petstore operations"""
    
    def __init__(self):
        self.templates = {
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
    
    def get_prompt(self, template_name: str, **kwargs) -> Dict[str, str]:
        """Generate a prompt from template"""
        if template_name not in self.templates:
            raise ValueError(f"Unknown template: {template_name}")
        
        template = self.templates[template_name]
        
        return {
            "system": template.system,
            "user": template.user_template.format(**kwargs)
        }
    
    def add_template(self, name: str, template: PromptTemplate):
        """Add a new prompt template"""
        self.templates[name] = template
