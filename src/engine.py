"""
Game engine module for PixelPrompt.

Handles the main game loop, event processing, camera system, and rendering.
"""

import pygame
import logging
from typing import Dict, List, Optional, Tuple

from src.world import World
from src.entities import Agent, AgentState
from src.config_manager import get_window_size, get_fps_target

logger = logging.getLogger("pixelprompt.engine")


class GameEngine:
    """
    Main game engine managing the game loop, rendering, and state.

    The engine coordinates all game systems including world rendering,
    camera control, and entity management.
    """

    def __init__(self, config: Dict) -> None:
        """
        Initialize the game engine.

        Args:
            config: Configuration dictionary from config_manager
        """
        logger.info("Initializing game engine...")

        # Store config
        self.config = config

        # Initialize pygame
        pygame.init()
        logger.info("pygame initialized")

        # Create window
        window_width, window_height = get_window_size(config)
        window_flags = pygame.RESIZABLE if config['window'].get('resizable', True) else 0
        self.screen = pygame.display.set_mode((window_width, window_height), window_flags)
        pygame.display.set_caption("PixelPrompt")
        logger.info(f"Window created: {window_width}x{window_height}")

        # Create clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps_target = get_fps_target(config)

        # Camera system
        self.camera_offset = pygame.math.Vector2(0, 0)
        self.pan_speed = config['camera']['pan_speed']
        self.camera_bounds = config['camera']['bounds']

        # World
        self.world = World(config)

        # Initialize agents from config
        self.agents: List[Agent] = []
        self.selected_agent: Optional[Agent] = None

        for agent_config in config.get('agents', []):
            agent = Agent(agent_config, config['camera']['bounds'])
            self.agents.append(agent)
            logger.info(f"Created agent: {agent.name} (id={agent.id})")

        # Engine state
        self.running = True

        logger.info(f"Game engine initialized successfully with {len(self.agents)} agent(s)")

    def run(self) -> None:
        """
        Main game loop.

        Runs until the user quits the game. Handles events, updates game state,
        and renders each frame at the target FPS.
        """
        logger.info("Starting game loop...")

        while self.running:
            # Calculate delta time in seconds (CRITICAL: convert ms to seconds)
            dt = self.clock.tick(self.fps_target) / 1000.0

            # Process events
            self.handle_events()

            # Update game state
            self.update(dt)

            # Render frame
            self.render()

        # Cleanup
        logger.info("Game loop ended, shutting down...")
        pygame.quit()

    def handle_events(self) -> None:
        """
        Process pygame events.

        Handles window close, keyboard input, and mouse events.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Quit event received")
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("ESC key pressed, exiting")
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_agent_click(event.pos)

    def _handle_agent_click(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Handle agent selection via mouse click.

        Args:
            mouse_pos: Mouse position in screen coordinates
        """
        # Check each agent for click (reverse order for top-most first)
        for agent in reversed(self.agents):
            if agent.handle_click(mouse_pos, self.camera_offset):
                # Deselect previous agent
                if self.selected_agent:
                    self.selected_agent.selected = False

                # Select new agent
                self.selected_agent = agent
                agent.selected = True
                logger.info(f"Selected agent: {agent.name}")
                break

    def update(self, dt: float) -> None:
        """
        Update game state.

        Args:
            dt: Delta time in seconds since last frame
        """
        # Update camera based on keyboard input
        self.update_camera(dt)

        # Update all agents
        for agent in self.agents:
            agent.update(dt)

    def update_camera(self, dt: float) -> None:
        """
        Update camera position based on WASD input.

        Camera movement is clamped to world bounds to prevent viewing
        outside the playable area.

        Args:
            dt: Delta time in seconds since last frame
        """
        keys = pygame.key.get_pressed()

        # Calculate movement distance for this frame
        move_distance = self.pan_speed * dt * 60  # Scale for consistent speed at 60 FPS

        # WASD movement
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.camera_offset.y -= move_distance
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.camera_offset.y += move_distance
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.camera_offset.x -= move_distance
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.camera_offset.x += move_distance

        # Clamp camera to world bounds
        # CRITICAL: Use max() for minimum bounds, min() for maximum bounds
        screen_width, screen_height = self.screen.get_size()

        # Minimum bounds (can't pan before world start)
        self.camera_offset.x = max(self.camera_bounds['min_x'], self.camera_offset.x)
        self.camera_offset.y = max(self.camera_bounds['min_y'], self.camera_offset.y)

        # Maximum bounds (can't pan beyond world end)
        max_camera_x = self.camera_bounds['max_x'] - screen_width
        max_camera_y = self.camera_bounds['max_y'] - screen_height
        self.camera_offset.x = min(max_camera_x, self.camera_offset.x)
        self.camera_offset.y = min(max_camera_y, self.camera_offset.y)

    def render(self) -> None:
        """
        Render the current game state.

        Rendering order:
        1. Background color
        2. World (tiles)
        3. Agents (Phase 2)
        4. UI (Phase 4)
        5. Flip display
        """
        # Fill background
        bg_color = pygame.Color(self.config['colors']['background'])
        self.screen.fill(bg_color)

        # Render world
        self.world.render(self.screen, self.camera_offset)

        # Render all agents
        for agent in self.agents:
            agent.render(self.screen, self.camera_offset)

        # Flip display to show rendered frame
        pygame.display.flip()

    def get_camera_offset(self) -> pygame.math.Vector2:
        """
        Get the current camera offset.

        Returns:
            Current camera offset as Vector2
        """
        return self.camera_offset.copy()
