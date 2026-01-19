"""Configuration management with validation and defaults."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import os

logger = logging.getLogger("pixelprompt.config")


def get_default_config() -> Dict[str, Any]:
    """
    Generate default configuration.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "version": "2.0",
        "window": {
            "width": 1280,
            "height": 720,
            "resizable": True,
            "fps_target": 60
        },
        "llm_providers": {
            "ollama": {
                "enabled": True,
                "base_url": "http://localhost:11434",
                "default_model": "llama3.2:3b",
                "timeout_seconds": 30,
                "health_check_endpoint": "/api/tags"
            },
            "gemini": {
                "enabled": False,
                "api_key_env": "GEMINI_API_KEY",
                "default_model": "gemini-2.0-flash-exp",
                "rate_limit_rpm": 60
            },
            "claude": {
                "enabled": False,
                "api_key_env": "ANTHROPIC_API_KEY",
                "default_model": "claude-sonnet-4-5-20250929",
                "rate_limit_rpm": 50
            }
        },
        "agents": [
            {
                "id": "agent_001",
                "name": "Pixel",
                "provider": "ollama",
                "model": "llama3.2:3b",
                "spawn_position": [640, 360],
                "color_hex": "#7DCFB6",
                "system_prompt": "You are Pixel, a helpful assistant who lives in a virtual room. Keep responses concise and friendly (1-2 sentences).",
                "max_history": 10
            }
        ],
        "camera": {
            "pan_speed": 5,
            "bounds": {
                "min_x": 0,
                "min_y": 0,
                "max_x": 2000,
                "max_y": 2000
            }
        },
        "ui": {
            "input_box_height": 50,
            "bubble_max_width": 300,
            "bubble_padding": 10,
            "typewriter_delay_ms": 30
        },
        "colors": {
            "background": "#2E2E3A",
            "ui_panel": "#3D3D4D",
            "accent_mint": "#7DCFB6",
            "accent_coral": "#F79D84",
            "accent_butter": "#FBD87F",
            "text": "#E8E8E8",
            "error": "#E57373"
        }
    }


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file with validation.
    
    If file doesn't exist, creates it with defaults.
    If file is malformed, backs it up and creates new default.
    
    Args:
        config_path: Path to config file
        
    Returns:
        Configuration dictionary
        
    Raises:
        ValueError: If config validation fails
    """
    config_file = Path(config_path)
    
    # Create default config if file doesn't exist
    if not config_file.exists():
        logger.info(f"Config file not found at {config_path}, creating default")
        config = get_default_config()
        save_config(config_path, config)
        return config
    
    # Try to load existing config
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        logger.info(f"Loaded config from {config_path}")
        
        # Validate and merge with defaults (in case new fields added)
        config = merge_with_defaults(config)
        
        # Validate the merged config
        validate_config(config)
        
        return config
        
    except json.JSONDecodeError as e:
        logger.error(f"Malformed config file: {e}")
        
        # Backup corrupted file
        backup_path = config_file.with_suffix('.json.backup')
        config_file.rename(backup_path)
        logger.info(f"Backed up corrupted config to {backup_path}")
        
        # Create new default
        config = get_default_config()
        save_config(config_path, config)
        logger.info(f"Created new default config at {config_path}")
        
        return config
        
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise


def save_config(config_path: str, config: Dict[str, Any]) -> None:
    """
    Save configuration to JSON file.
    
    Args:
        config_path: Path to save config
        config: Configuration dictionary
    """
    config_file = Path(config_path)
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved config to {config_path}")
        
    except Exception as e:
        logger.error(f"Error saving config: {e}")
        raise


def merge_with_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge user config with defaults to ensure all fields exist.
    
    Args:
        config: User configuration
        
    Returns:
        Merged configuration
    """
    defaults = get_default_config()
    
    def deep_merge(base: Dict, override: Dict) -> Dict:
        """Recursively merge dictionaries."""
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    return deep_merge(defaults, config)


def validate_config(config: Dict[str, Any]) -> None:
    """
    Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary
        
    Raises:
        ValueError: If validation fails
    """
    # Check required top-level keys
    required_keys = ["version", "window", "llm_providers", "agents", "camera", "ui"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    # Validate window config
    window = config["window"]
    if not (100 <= window["width"] <= 7680):
        raise ValueError(f"Invalid window width: {window['width']}")
    if not (100 <= window["height"] <= 4320):
        raise ValueError(f"Invalid window height: {window['height']}")
    if not (10 <= window["fps_target"] <= 240):
        raise ValueError(f"Invalid FPS target: {window['fps_target']}")
    
    # Validate at least one enabled provider
    providers = config["llm_providers"]
    enabled_providers = [name for name, cfg in providers.items() if cfg.get("enabled", False)]
    
    if not enabled_providers:
        logger.warning("No LLM providers enabled - you won't be able to chat with agents")
    
    # Validate agents
    if not config["agents"]:
        raise ValueError("Must have at least one agent configured")
    
    for agent in config["agents"]:
        # Check required fields
        required_agent_keys = ["id", "name", "provider", "model", "spawn_position", "color_hex"]
        for key in required_agent_keys:
            if key not in agent:
                raise ValueError(f"Agent missing required field: {key}")
        
        # Validate provider exists
        if agent["provider"] not in providers:
            raise ValueError(f"Agent uses unknown provider: {agent['provider']}")
        
        # Validate color hex
        color = agent["color_hex"]
        if not (color.startswith("#") and len(color) == 7):
            raise ValueError(f"Invalid color hex: {color}")
    
    logger.debug("Config validation passed")


def get_window_size(config: Dict[str, Any]) -> Tuple[int, int]:
    """
    Get window dimensions from config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Tuple of (width, height)
    """
    return (config["window"]["width"], config["window"]["height"])


def get_fps_target(config: Dict[str, Any]) -> int:
    """
    Get target FPS from config.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Target FPS
    """
    return config["window"]["fps_target"]


def get_enabled_providers(config: Dict[str, Any]) -> Dict[str, Dict]:
    """
    Get dictionary of enabled providers with their configs.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict mapping provider names to their configurations
    """
    providers = config["llm_providers"]
    return {
        name: cfg 
        for name, cfg in providers.items() 
        if cfg.get("enabled", False)
    }


def check_provider_credentials(config: Dict[str, Any]) -> Dict[str, bool]:
    """
    Check if API keys exist for enabled cloud providers.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Dict mapping provider names to credential availability
    """
    results = {}
    
    for name, cfg in config["llm_providers"].items():
        if not cfg.get("enabled", False):
            continue
        
        # Ollama doesn't need credentials
        if name == "ollama":
            results[name] = True
            continue
        
        # Check for API key in environment
        api_key_env = cfg.get("api_key_env")
        if api_key_env:
            api_key = os.getenv(api_key_env)
            results[name] = bool(api_key and len(api_key) > 0)
        else:
            results[name] = False
    
    return results
