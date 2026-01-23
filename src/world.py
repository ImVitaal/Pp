"""World rendering and management for PixelPrompt.

Handles the tiled floor and environment rendering.
"""

import pygame
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class World:
    """Manages the game world, tilemap, and environment."""

    def __init__(self, config: Dict):
        """
        Initialize world from config.

        Args:
            config: Configuration dictionary
        """
        self.tile_size = 32
        self.floor_color = pygame.Color("#3D3D4D")  # Charcoal
        self.grid_color = pygame.Color("#2E2E3A")   # Slate

        # Calculate world size from camera bounds
        bounds = config['camera']['bounds']
        self.width = bounds['max_x']
        self.height = bounds['max_y']

        logger.info(f"World initialized: {self.width}x{self.height}px")

    def render(self, surface: pygame.Surface,
               camera_offset: pygame.math.Vector2) -> None:
        """
        Draw tiled floor with camera offset applied.

        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera position for viewport scrolling
        """
        screen_width, screen_height = surface.get_size()

        # Calculate visible tile range
        start_x = int(camera_offset.x // self.tile_size)
        start_y = int(camera_offset.y // self.tile_size)
        end_x = start_x + (screen_width // self.tile_size) + 2
        end_y = start_y + (screen_height // self.tile_size) + 2

        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * self.tile_size - camera_offset.x
                screen_y = y * self.tile_size - camera_offset.y

                # Draw tile
                pygame.draw.rect(
                    surface,
                    self.floor_color,
                    (screen_x, screen_y, self.tile_size, self.tile_size)
                )

                # Draw grid lines
                pygame.draw.rect(
                    surface,
                    self.grid_color,
                    (screen_x, screen_y, self.tile_size, self.tile_size),
                    1  # 1px border
                )
