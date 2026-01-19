"""Ollama provider for local LLM inference."""

import json
import logging
from typing import Generator, List, Dict
import requests

from . import BaseLLMProvider

logger = logging.getLogger("pixelprompt.llm.ollama")


class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider for free, offline inference."""
    
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 30):
        """
        Initialize Ollama provider.
        
        Args:
            base_url: Base URL for Ollama API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        logger.info(f"Initialized OllamaProvider with base_url={self.base_url}")
    
    @property
    def name(self) -> str:
        """Provider display name."""
        return "Ollama"
    
    def send_message(self, 
                    messages: List[Dict[str, str]], 
                    model: str,
                    **kwargs) -> Generator[str, None, None]:
        """
        Stream responses from Ollama's /api/chat endpoint.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name (e.g., "llama3.2:3b")
            **kwargs: Additional options (temperature, top_p, etc.)
            
        Yields:
            str: Text chunks from the model
            
        Raises:
            ConnectionError: Cannot reach Ollama server
            TimeoutError: Request timed out
            ValueError: Invalid model name
        """
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        # Add optional parameters
        if kwargs:
            payload.update(kwargs)
        
        logger.debug(f"Sending request to {url} with model={model}")
        
        try:
            response = requests.post(
                url, 
                json=payload, 
                stream=True, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Stream chunks
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        
                        # Extract content from message
                        if 'message' in chunk and 'content' in chunk['message']:
                            content = chunk['message']['content']
                            if content:  # Only yield non-empty content
                                yield content
                        
                        # Check if done
                        if chunk.get('done', False):
                            logger.debug("Stream completed")
                            break
                            
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse chunk: {e}")
                        continue
            
        except requests.ConnectionError as e:
            error_msg = f"Cannot reach Ollama at {self.base_url}"
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e
        
        except requests.Timeout as e:
            error_msg = f"Request timed out after {self.timeout}s"
            logger.error(error_msg)
            raise TimeoutError(error_msg) from e
        
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                error_msg = f"Model '{model}' not found. Run: ollama pull {model}"
                logger.error(error_msg)
                raise ValueError(error_msg) from e
            else:
                logger.error(f"HTTP error: {e}")
                raise
    
    def is_available(self) -> bool:
        """
        Check if Ollama server is running.
        
        Returns:
            bool: True if server is reachable
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags", 
                timeout=5
            )
            available = response.status_code == 200
            
            if available:
                logger.debug("Ollama server is available")
            else:
                logger.warning(f"Ollama server returned status {response.status_code}")
            
            return available
            
        except requests.RequestException as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Get list of downloaded models from Ollama.
        
        Returns:
            List[str]: Model names
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            models = [m['name'] for m in data.get('models', [])]
            
            logger.debug(f"Available models: {models}")
            return models
            
        except requests.RequestException as e:
            logger.error(f"Failed to list models: {e}")
            return []
    
    def pull_model(self, model: str) -> bool:
        """
        Pull a model from Ollama registry (blocking operation).
        
        Args:
            model: Model name to pull
            
        Returns:
            bool: True if successful
        """
        url = f"{self.base_url}/api/pull"
        payload = {"name": model}
        
        logger.info(f"Pulling model: {model}")
        
        try:
            response = requests.post(
                url,
                json=payload,
                stream=True,
                timeout=300  # 5 minutes for large models
            )
            response.raise_for_status()
            
            # Stream progress updates
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line)
                        if 'status' in chunk:
                            logger.info(f"Pull status: {chunk['status']}")
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"Successfully pulled model: {model}")
            return True
            
        except requests.RequestException as e:
            logger.error(f"Failed to pull model: {e}")
            return False
