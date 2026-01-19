"""
World module for PixelPrompt.

Handles rendering the tiled floor and managing camera transformations.
"""

import pygame
import logging
from typing import Dict, Tuple

logger = logging.getLogger("pixelprompt.world")


class World:
    """
    Manages the tiled world and camera transformations.

    The world consists of a 32x32 pixel tile grid. Only tiles visible
    in the current viewport are rendered for performance.
    """

    def __init__(self, config: Dict) -> None:
        """
        Initialize the world from configuration.

        Args:
            config: Configuration dictionary containing camera bounds and colors
        """
        self.config = config

        # Tile configuration
        self.tile_size = 32  # pixels per tile (hardcoded)

        # Get world bounds from camera config
        bounds = config['camera']['bounds']
        self.min_x = bounds['min_x']
        self.min_y = bounds['min_y']
        self.max_x = bounds['max_x']
        self.max_y = bounds['max_y']

        # Calculate world dimensions in tiles
        self.world_width_tiles = (self.max_x - self.min_x) // self.tile_size
        self.world_height_tiles = (self.max_y - self.min_y) // self.tile_size

        # Colors from config
        self.floor_color = pygame.Color(config['colors']['ui_panel'])  # #3D3D4D
        self.grid_color = pygame.Color(config['colors']['background'])  # #2E2E3A

        logger.info(f"World initialized: {self.world_width_tiles}x{self.world_height_tiles} tiles "
                   f"({self.max_x}x{self.max_y} pixels)")

    def render(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2) -> None:
        """
        Render the visible portion of the tiled world.

        Only tiles visible in the current viewport are rendered for performance.
        Tiles are drawn with a subtle grid pattern.

        Args:
            surface: pygame Surface to render onto
            camera_offset: Current camera position offset
        """
        screen_width, screen_height = surface.get_size()

        # Calculate visible tile range
        start_tile_x, start_tile_y, end_tile_x, end_tile_y = self._get_visible_tile_range(
            (screen_width, screen_height),
            camera_offset
        )

        # Render visible tiles
        for tile_y in range(start_tile_y, end_tile_y):
            for tile_x in range(start_tile_x, end_tile_x):
                # Calculate world position
                world_x = tile_x * self.tile_size
                world_y = tile_y * self.tile_size

                # Transform to screen position
                screen_x = world_x - camera_offset.x
                screen_y = world_y - camera_offset.y

                # Create tile rectangle
                tile_rect = pygame.Rect(
                    int(screen_x),
                    int(screen_y),
                    self.tile_size,
                    self.tile_size
                )

                # Draw tile floor
                pygame.draw.rect(surface, self.floor_color, tile_rect)

                # Draw grid line (1px border)
                pygame.draw.rect(surface, self.grid_color, tile_rect, 1)

    def _get_visible_tile_range(
        self,
        screen_size: Tuple[int, int],
        camera_offset: pygame.math.Vector2
    ) -> Tuple[int, int, int, int]:
        """
        Calculate which tiles are visible in the current viewport.

        Args:
            screen_size: (width, height) of the viewport
            camera_offset: Current camera position

        Returns:
            Tuple of (start_x, start_y, end_x, end_y) tile indices
        """
        screen_width, screen_height = screen_size

        # Calculate starting tile (top-left of viewport)
        start_tile_x = int(camera_offset.x // self.tile_size)
        start_tile_y = int(camera_offset.y // self.tile_size)

        # Calculate ending tile (bottom-right of viewport)
        # Add 2 to account for partial tiles at edges
        end_tile_x = start_tile_x + (screen_width // self.tile_size) + 2
        end_tile_y = start_tile_y + (screen_height // self.tile_size) + 2

        # Clamp to world bounds
        start_tile_x = max(0, start_tile_x)
        start_tile_y = max(0, start_tile_y)
        end_tile_x = min(self.world_width_tiles, end_tile_x)
        end_tile_y = min(self.world_height_tiles, end_tile_y)

        return start_tile_x, start_tile_y, end_tile_x, end_tile_y

    def get_bounds(self) -> Dict[str, int]:
        """
        Get the world boundaries.

        Returns:
            Dictionary with min_x, min_y, max_x, max_y keys
        """
        return {
            'min_x': self.min_x,
            'min_y': self.min_y,
            'max_x': self.max_x,
            'max_y': self.max_y
        }
