#!/usr/bin/env python3
"""
Sampling configurations for different AI model interactions
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class SamplingConfig:
    """Configuration for AI model sampling parameters"""
    temperature: float = 0.3
    top_p: float = 0.9
    max_tokens: int = 1500
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1
    stop_sequences: Optional[list] = None


class SamplingManager:
    """Manages different sampling configurations"""
    
    def __init__(self):
        self.configs = {
            "conservative": SamplingConfig(
                temperature=0.1,
                top_p=0.9,
                max_tokens=1000,
                frequency_penalty=0.0,
                presence_penalty=0.0
            ),
            
            "balanced": SamplingConfig(
                temperature=0.3,
                top_p=0.9,
                max_tokens=1500,
                frequency_penalty=0.1,
                presence_penalty=0.1
            ),
            
            "creative": SamplingConfig(
                temperature=0.7,
                top_p=0.95,
                max_tokens=2000,
                frequency_penalty=0.2,
                presence_penalty=0.2
            ),
            
            "precise": SamplingConfig(
                temperature=0.0,
                top_p=1.0,
                max_tokens=800,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        }
    
    def get_config(self, config_name: str) -> SamplingConfig:
        """Get sampling configuration by name"""
        if config_name not in self.configs:
            return self.configs["balanced"]  # Default
        return self.configs[config_name]
    
    def get_config_dict(self, config_name: str) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        config = self.get_config(config_name)
        return {
            "temperature": config.temperature,
            "top_p": config.top_p,
            "max_tokens": config.max_tokens,
            "frequency_penalty": config.frequency_penalty,
            "presence_penalty": config.presence_penalty,
            "stop": config.stop_sequences
        }
    
    def add_config(self, name: str, config: SamplingConfig):
        """Add new sampling configuration"""
        self.configs[name] = config
