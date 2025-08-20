#!/usr/bin/env python3
"""
Configuration management for the financial audit system
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import os

@dataclass
class ModelConfig:
    """Model configuration"""
    name: str
    provider: str  # 'gemini', 'ollama'
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 8000
    max_retries: int = 2

@dataclass
class AgentConfig:
    """Individual agent configuration"""
    agent_id: str
    temperature: float
    max_tokens: int
    approach: str

@dataclass
class SystemConfig:
    """System-wide configuration"""
    max_retries: int = 2
    consensus_tolerance: float = 0.0001  # 0.01% for strict consensus
    input_dir: str = "input"
    output_dir: str = "results"
    enable_debug: bool = False

class ConfigManager:
    """Configuration manager for the audit system"""
    
    GEMINI_MODELS = {
        "gemini-1.5-flash": "gemini-1.5-flash",
        "gemini-2.0-flash": "gemini-2.0-flash-thinking-exp"
    }
    
    OLLAMA_MODELS = {
        "qwen3:4b": "qwen3:4b",
        "gemma3n:e2b": "gemma3n:e2b", 
        "qwen2.5:4b": "qwen2.5:4b",
        "llama3.2:3b": "llama3.2:3b"
    }
    
    AGENT_CONFIGS = {
        "agent_1": AgentConfig(
            agent_id="agent_1",
            temperature=0.0,
            max_tokens=8000,
            approach="Focus on systematic line-by-line verification of all calculations."
        ),
        "agent_2": AgentConfig(
            agent_id="agent_2", 
            temperature=0.05,
            max_tokens=7000,
            approach="Emphasize cross-checking totals against component sums."
        ),
        "agent_3": AgentConfig(
            agent_id="agent_3",
            temperature=0.0,
            max_tokens=8000,
            approach="Comprehensive validation including balance sheet equation verification."
        )
    }
    
    @classmethod
    def create_gemini_config(cls, model_name: str = "gemini-2.0-flash", 
                           api_key: str = None) -> ModelConfig:
        """Create Gemini model configuration"""
        
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY", "AIzaSyCjYSIkha4ZAeIR7yXe3TH4Pk7Ko8gJmZU")
        
        model_id = cls.GEMINI_MODELS.get(model_name, model_name)
        
        return ModelConfig(
            name=model_id,
            provider="gemini",
            api_key=api_key,
            temperature=0.0,
            max_tokens=8000,
            max_retries=2
        )
    
    @classmethod
    def create_ollama_config(cls, model_name: str = "qwen3:4b", 
                           base_url: str = "http://localhost:11434") -> ModelConfig:
        """Create Ollama model configuration"""
        
        model_id = cls.OLLAMA_MODELS.get(model_name, model_name)
        
        return ModelConfig(
            name=model_id,
            provider="ollama",
            base_url=base_url,
            temperature=0.0,
            max_tokens=8000,
            max_retries=2
        )
    
    @classmethod
    def create_system_config(cls, **kwargs) -> SystemConfig:
        """Create system configuration"""
        return SystemConfig(**kwargs)
    
    @classmethod
    def get_agent_config(cls, agent_id: str) -> AgentConfig:
        """Get configuration for specific agent"""
        return cls.AGENT_CONFIGS.get(agent_id, cls.AGENT_CONFIGS["agent_1"])
    
    @classmethod
    def list_available_models(cls) -> Dict[str, Dict[str, str]]:
        """List all available models"""
        return {
            "gemini": cls.GEMINI_MODELS,
            "ollama": cls.OLLAMA_MODELS
        }
    
    @classmethod
    def validate_config(cls, model_config: ModelConfig) -> bool:
        """Validate model configuration"""
        
        if model_config.provider == "gemini":
            if not model_config.api_key:
                print("❌ Gemini API key required")
                return False
            if model_config.name not in cls.GEMINI_MODELS.values():
                print(f"⚠️  Unknown Gemini model: {model_config.name}")
        
        elif model_config.provider == "ollama":
            if not model_config.base_url:
                print("❌ Ollama base URL required")
                return False
            # Could add Ollama connectivity check here
        
        else:
            print(f"❌ Unknown provider: {model_config.provider}")
            return False
        
        return True