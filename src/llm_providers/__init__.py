"""LLM Provider abstraction layer for multiple backends."""

from abc import ABC, abstractmethod
from typing import List, Dict, Generator, Optional
import logging
import os

logger = logging.getLogger("pixelprompt.llm")


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM backends."""
    
    @abstractmethod
    def send_message(self, 
                    messages: List[Dict[str, str]], 
                    model: str,
                    **kwargs) -> Generator[str, None, None]:
        """
        Stream response tokens from the LLM.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model identifier (e.g., "llama3.2:3b")
            **kwargs: Provider-specific options
            
        Yields:
            str: Text chunks as they arrive
            
        Raises:
            ConnectionError: Provider unreachable
            ValueError: Invalid model or parameters
            TimeoutError: Request exceeded timeout
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Health check for this provider.
        
        Returns:
            bool: True if provider is reachable and configured
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Return available model names.
        
        Returns:
            List[str]: Model identifiers that can be used with send_message
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name (e.g., "Ollama", "Google Gemini")."""
        pass


def create_provider(provider_name: str, config: Dict) -> BaseLLMProvider:
    """
    Factory function to instantiate LLM providers.
    
    Args:
        provider_name: Name of provider ("ollama", "gemini", "claude")
        config: Provider configuration dictionary
        
    Returns:
        Initialized provider instance
        
    Raises:
        ValueError: If provider name is unknown
        ImportError: If provider dependencies not installed
    """
    if provider_name == "ollama":
        from .ollama import OllamaProvider
        return OllamaProvider(
            base_url=config.get("base_url", "http://localhost:11434"),
            timeout=config.get("timeout_seconds", 30)
        )
    
    elif provider_name == "gemini":
        try:
            from .gemini import GeminiProvider
        except ImportError as e:
            # Distinguish between missing module (not implemented) and missing pip package
            if "gemini" in str(e).lower() and "no module" in str(e).lower():
                raise NotImplementedError(
                    "Gemini provider is not yet implemented (Phase 6). "
                    "Use 'ollama' provider for now, or contribute the implementation!"
                )
            raise ImportError(
                "Gemini provider requires: pip install google-generativeai>=0.8.0"
            )

        api_key_env = config.get("api_key_env", "GEMINI_API_KEY")
        api_key = os.getenv(api_key_env)

        if not api_key or not api_key.strip():
            raise ValueError(
                f"Gemini API key not found or empty in environment variable: {api_key_env}"
            )

        return GeminiProvider(api_key=api_key.strip())

    elif provider_name == "claude":
        try:
            from .claude import ClaudeProvider
        except ImportError as e:
            # Distinguish between missing module (not implemented) and missing pip package
            if "claude" in str(e).lower() and "no module" in str(e).lower():
                raise NotImplementedError(
                    "Claude provider is not yet implemented (Phase 6). "
                    "Use 'ollama' provider for now, or contribute the implementation!"
                )
            raise ImportError(
                "Claude provider requires: pip install anthropic>=0.39.0"
            )

        api_key_env = config.get("api_key_env", "ANTHROPIC_API_KEY")
        api_key = os.getenv(api_key_env)

        if not api_key or not api_key.strip():
            raise ValueError(
                f"Claude API key not found or empty in environment variable: {api_key_env}"
            )

        return ClaudeProvider(api_key=api_key.strip())
    
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


__all__ = ["BaseLLMProvider", "create_provider"]
