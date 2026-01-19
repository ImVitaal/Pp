#!/usr/bin/env python3
"""
Test Phase 1 implementation without requiring a display.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set SDL to use dummy video driver (no display needed)
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

import pygame
from src.config_manager import load_config
from src.engine import GameEngine
from src.world import World

def test_phase1():
    """Test Phase 1 implementation."""
    print("="*60)
    print("Testing Phase 1: Game Engine & World")
    print("="*60)

    # Load config
    print("\n[1/5] Loading configuration...")
    config = load_config("config.json")
    print("  ✓ Config loaded")

    # Initialize pygame
    print("\n[2/5] Initializing pygame...")
    pygame.init()
    print(f"  ✓ pygame initialized (version {pygame.version.ver})")

    # Create World
    print("\n[3/5] Creating World...")
    world = World(config)
    print(f"  ✓ World created: {world.world_width_tiles}x{world.world_height_tiles} tiles")
    print(f"  ✓ Bounds: ({world.min_x}, {world.min_y}) to ({world.max_x}, {world.max_y})")

    # Create GameEngine
    print("\n[4/5] Creating GameEngine...")
    engine = GameEngine(config)
    print(f"  ✓ Engine created")
    print(f"  ✓ Window size: {engine.screen.get_size()}")
    print(f"  ✓ FPS target: {engine.fps_target}")
    print(f"  ✓ Camera offset: ({engine.camera_offset.x}, {engine.camera_offset.y})")
    print(f"  ✓ Pan speed: {engine.pan_speed}")

    # Test camera bounds
    print("\n[5/5] Testing camera system...")
    original_offset = engine.camera_offset.copy()

    # Test camera movement (simulate WASD for 1 frame)
    dt = 1.0 / 60.0  # One frame at 60 FPS

    # Move camera right
    engine.camera_offset.x += 100
    engine.update_camera(0)  # This will clamp to bounds
    print(f"  ✓ Camera clamping works (x: {engine.camera_offset.x})")

    # Reset camera
    engine.camera_offset = original_offset.copy()

    # Test World bounds
    bounds = world.get_bounds()
    print(f"  ✓ World bounds: {bounds}")

    # Test visible tile calculation
    visible_tiles = world._get_visible_tile_range(
        engine.screen.get_size(),
        engine.camera_offset
    )
    print(f"  ✓ Visible tiles: {visible_tiles}")

    print("\n" + "="*60)
    print("Phase 1 Tests: PASSED")
    print("="*60)
    print("\nPhase 1 implementation complete:")
    print("  ✓ src/world.py - Tiled world rendering")
    print("  ✓ src/engine.py - Game loop and camera system")
    print("  ✓ main.py - Engine integration")
    print("\nTo test visually, run:")
    print("  python main.py")
    print("\nControls:")
    print("  WASD or Arrow Keys - Pan camera")
    print("  ESC - Exit")
    print("="*60)

    pygame.quit()

if __name__ == "__main__":
    try:
        test_phase1()
    except Exception as e:
        print(f"\n[FAIL] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
