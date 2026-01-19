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


def test_validate_config_invalid_hex_color():
    """Test validation catches invalid hex colors."""
    config = get_default_config()
    config["agents"][0]["color_hex"] = "#GGGGGG"  # Invalid hex digits

    with pytest.raises(ValueError, match="Invalid color hex"):
        validate_config(config)


def test_validate_config_invalid_hex_color_short():
    """Test validation catches short hex colors."""
    config = get_default_config()
    config["agents"][0]["color_hex"] = "#ABC"  # Too short

    with pytest.raises(ValueError, match="Invalid color hex"):
        validate_config(config)


def test_validate_config_valid_hex_colors():
    """Test various valid hex color formats."""
    config = get_default_config()

    valid_colors = ["#000000", "#FFFFFF", "#7DCFB6", "#aabbcc", "#AABBCC", "#123456"]
    for color in valid_colors:
        config["agents"][0]["color_hex"] = color
        validate_config(config)  # Should not raise


def test_validate_config_invalid_spawn_position_type():
    """Test validation catches non-list spawn position."""
    config = get_default_config()
    config["agents"][0]["spawn_position"] = "640, 360"  # String, not list

    with pytest.raises(ValueError, match="spawn_position must be"):
        validate_config(config)


def test_validate_config_invalid_spawn_position_length():
    """Test validation catches wrong length spawn position."""
    config = get_default_config()
    config["agents"][0]["spawn_position"] = [640]  # Only one coordinate

    with pytest.raises(ValueError, match="spawn_position must be"):
        validate_config(config)


def test_validate_config_invalid_spawn_position_non_numeric():
    """Test validation catches non-numeric spawn position."""
    config = get_default_config()
    config["agents"][0]["spawn_position"] = ["a", "b"]  # Non-numeric

    with pytest.raises(ValueError, match="must be numbers"):
        validate_config(config)


def test_validate_config_negative_spawn_position():
    """Test validation catches negative spawn coordinates."""
    config = get_default_config()
    config["agents"][0]["spawn_position"] = [-100, 360]

    with pytest.raises(ValueError, match="negative coordinates"):
        validate_config(config)


def test_validate_config_valid_spawn_positions():
    """Test various valid spawn positions."""
    config = get_default_config()

    valid_positions = [[0, 0], [640, 360], [1000.5, 500.5], [0, 100]]
    for pos in valid_positions:
        config["agents"][0]["spawn_position"] = pos
        validate_config(config)  # Should not raise


def test_validate_config_inverted_camera_bounds_x():
    """Test validation catches inverted camera bounds (min_x >= max_x)."""
    config = get_default_config()
    config["camera"]["bounds"]["min_x"] = 2000
    config["camera"]["bounds"]["max_x"] = 0

    with pytest.raises(ValueError, match="min_x.*must be less than.*max_x"):
        validate_config(config)


def test_validate_config_inverted_camera_bounds_y():
    """Test validation catches inverted camera bounds (min_y >= max_y)."""
    config = get_default_config()
    config["camera"]["bounds"]["min_y"] = 2000
    config["camera"]["bounds"]["max_y"] = 0

    with pytest.raises(ValueError, match="min_y.*must be less than.*max_y"):
        validate_config(config)


def test_validate_config_invalid_ollama_url():
    """Test validation catches invalid Ollama URL."""
    config = get_default_config()
    config["llm_providers"]["ollama"]["base_url"] = "not a valid url"

    with pytest.raises(ValueError, match="Invalid Ollama"):
        validate_config(config)


def test_validate_config_invalid_ollama_url_scheme():
    """Test validation catches non-http(s) Ollama URL."""
    config = get_default_config()
    config["llm_providers"]["ollama"]["base_url"] = "ftp://localhost:11434"

    with pytest.raises(ValueError, match="http or https"):
        validate_config(config)


def test_check_provider_credentials_whitespace_key():
    """Test that whitespace-only API keys are rejected."""
    config = get_default_config()
    config["llm_providers"]["gemini"]["enabled"] = True
    os.environ["GEMINI_API_KEY"] = "   "  # Whitespace only

    results = check_provider_credentials(config)
    assert results.get("gemini", True) is False

    del os.environ["GEMINI_API_KEY"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
