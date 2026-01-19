"""Tests for config_manager module."""

import pytest
import json
from pathlib import Path
import tempfile
import os

from src.config_manager import (
    get_default_config,
    load_config,
    save_config,
    validate_config,
    merge_with_defaults,
    get_window_size,
    check_provider_credentials
)


def test_get_default_config():
    """Test default configuration generation."""
    config = get_default_config()
    
    # Check top-level keys
    assert "version" in config
    assert "window" in config
    assert "llm_providers" in config
    assert "agents" in config
    assert "camera" in config
    assert "ui" in config
    
    # Check window defaults
    assert config["window"]["width"] == 1280
    assert config["window"]["height"] == 720
    assert config["window"]["fps_target"] == 60
    
    # Check at least one agent exists
    assert len(config["agents"]) > 0
    assert config["agents"][0]["name"] == "Pixel"


def test_validate_config_valid():
    """Test validation of valid config."""
    config = get_default_config()
    validate_config(config)  # Should not raise


def test_validate_config_missing_key():
    """Test validation catches missing keys."""
    config = get_default_config()
    del config["window"]
    
    with pytest.raises(ValueError, match="Missing required config key"):
        validate_config(config)


def test_validate_config_invalid_window_size():
    """Test validation catches invalid window dimensions."""
    config = get_default_config()
    config["window"]["width"] = 50  # Too small
    
    with pytest.raises(ValueError, match="Invalid window width"):
        validate_config(config)


def test_validate_config_no_agents():
    """Test validation requires at least one agent."""
    config = get_default_config()
    config["agents"] = []
    
    with pytest.raises(ValueError, match="Must have at least one agent"):
        validate_config(config)


def test_save_and_load_config():
    """Test saving and loading configuration."""
    config = get_default_config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "test_config.json"
        
        # Save
        save_config(str(config_path), config)
        assert config_path.exists()
        
        # Load
        loaded = load_config(str(config_path))
        assert loaded == config


def test_merge_with_defaults():
    """Test merging user config with defaults."""
    defaults = get_default_config()
    
    # User config with partial data
    user_config = {
        "window": {
            "width": 1920,
            "height": 1080
        }
    }
    
    merged = merge_with_defaults(user_config)
    
    # User values preserved
    assert merged["window"]["width"] == 1920
    assert merged["window"]["height"] == 1080
    
    # Default values added
    assert "fps_target" in merged["window"]
    assert "agents" in merged


def test_get_window_size():
    """Test window size getter."""
    config = get_default_config()
    width, height = get_window_size(config)
    
    assert width == 1280
    assert height == 720


def test_check_provider_credentials():
    """Test API key checking."""
    config = get_default_config()
    
    # Enable Gemini with fake API key
    config["llm_providers"]["gemini"]["enabled"] = True
    os.environ["GEMINI_API_KEY"] = "test_key"
    
    results = check_provider_credentials(config)
    
    # Ollama doesn't need credentials
    assert results.get("ollama", False) == True
    
    # Gemini should find the env var
    assert results.get("gemini", False) == True
    
    # Cleanup
    del os.environ["GEMINI_API_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
