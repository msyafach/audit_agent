"""
Agent implementations for different model providers
"""

from .gemini_agent import GeminiFinancialAgent, GeminiTripleAgentSystem
from .ollama_agent import OllamaFinancialAgent, OllamaTripleAgentSystem

__all__ = [
    'GeminiFinancialAgent',
    'GeminiTripleAgentSystem',
    'OllamaFinancialAgent', 
    'OllamaTripleAgentSystem'
]