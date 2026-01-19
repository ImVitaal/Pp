"""
Entity module for PixelPrompt.

Contains the Agent class with autonomous state machine and animations.
"""

import pygame
import random
import math
import os
import logging
from enum import Enum
from typing import Dict, Optional, Tuple

logger = logging.getLogger("pixelprompt.entities")


class AgentState(Enum):
    """Agent behavioral states."""
    IDLE = "idle"
    THINKING = "thinking"
    TALKING = "talking"
    ERROR = "error"


class Agent(pygame.sprite.Sprite):
    """
    Autonomous agent with animated states.

    The agent can wander (IDLE), pace while thinking (THINKING),
    bob while talking (TALKING), or shake on errors (ERROR).
    """

    def __init__(self, config: Dict, world_bounds: Dict[str, int]) -> None:
        """
        Initialize an agent from configuration.

        Args:
            config: Agent configuration dictionary with id, name, spawn_position,
                   color_hex, provider, model, etc.
            world_bounds: World boundaries dict with min_x, min_y, max_x, max_y
        """
        super().__init__()

        # Identity
        self.id = config['id']
        self.name = config['name']
        self.provider_name = config.get('provider', 'unknown')
        self.model = config.get('model', 'unknown')

        # State management
        self.state = AgentState.IDLE
        self.state_timer = 0.0

        # Position & movement (CRITICAL: Use Vector2 for continuous positions)
        spawn_pos = config.get('spawn_position', [640, 360])
        self.position = pygame.math.Vector2(float(spawn_pos[0]), float(spawn_pos[1]))
        self.target_position = self.position.copy()
        self.move_speed = 50.0  # pixels per second

        # Store world bounds for clamping (CRITICAL: prevents escaping world)
        self.world_bounds = world_bounds

        # Visuals
        self.color = self._parse_color(config.get('color_hex', '#7DCFB6'))
        self.size = (20, 40)  # width, height in pixels
        self.selected = False

        # Animation state
        self.bob_offset = 0.0
        self.bob_base_y = self.position.y  # CRITICAL: For bob animation without drift
        self.error_base_pos = self.position.copy()  # CRITICAL: For shake animation without drift
        self.pace_direction = 1  # THINKING state pacing direction

        # Create sprite
        self._create_sprite()

        logger.info(f"Agent created: {self.name} (id={self.id}) at {self.position}")

    def _parse_color(self, color_hex: str) -> pygame.Color:
        """
        Parse hex color with fallback.

        Args:
            color_hex: Hex color string like "#7DCFB6"

        Returns:
            pygame.Color object
        """
        try:
            # Validate format
            if not color_hex.startswith('#') or len(color_hex) != 7:
                raise ValueError(f"Invalid hex format: {color_hex}")
            return pygame.Color(color_hex)
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid color '{color_hex}', using fallback #7DCFB6: {e}")
            return pygame.Color("#7DCFB6")

    def _create_sprite(self) -> None:
        """
        Create sprite surface with fallback to procedural rendering.

        Attempts to load sprite from assets/sprites/{agent_id}.png.
        If not found, creates a simple colored rectangle.
        """
        sprite_path = f"assets/sprites/{self.id}.png"

        if os.path.exists(sprite_path):
            try:
                self.image = pygame.image.load(sprite_path).convert_alpha()
                logger.info(f"Loaded sprite for {self.id} from {sprite_path}")
            except Exception as e:
                logger.warning(f"Failed to load sprite: {e}, using fallback")
                self._create_fallback_sprite()
        else:
            logger.debug(f"No sprite at {sprite_path}, using fallback rectangle")
            self._create_fallback_sprite()

        self.rect = self.image.get_rect()
        self.rect.center = (int(self.position.x), int(self.position.y))

    def _create_fallback_sprite(self) -> None:
        """Create a simple colored rectangle as fallback sprite."""
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.image.fill(self.color)

    def update(self, dt: float) -> None:
        """
        Update agent state and animation.

        Args:
            dt: Delta time in seconds since last frame
        """
        self.state_timer += dt

        # Dispatch to state-specific update
        if self.state == AgentState.IDLE:
            self._update_idle(dt)
        elif self.state == AgentState.THINKING:
            self._update_thinking(dt)
        elif self.state == AgentState.TALKING:
            self._update_talking(dt)
        elif self.state == AgentState.ERROR:
            self._update_error(dt)

        # Update sprite rect for collision detection
        self.rect.center = (int(self.position.x), int(self.position.y))

    def _update_idle(self, dt: float) -> None:
        """
        IDLE state: Random walks every 3-5 seconds.

        The agent picks a random nearby target and walks to it,
        then waits before picking a new target.
        """
        # Move toward target
        distance = self.position.distance_to(self.target_position)

        # BUG FIX: Check distance > 1 before normalizing (prevent zero vector crash)
        if distance > 1.0:
            direction = (self.target_position - self.position).normalize()
            move_distance = self.move_speed * dt
            # Don't overshoot the target
            if move_distance > distance:
                self.position = self.target_position.copy()
            else:
                self.position += direction * move_distance

        # Pick new target every 3-5 seconds after reaching current target
        elif self.state_timer > random.uniform(3.0, 5.0):
            self._pick_random_target()
            self.state_timer = 0.0

    def _update_thinking(self, dt: float) -> None:
        """
        THINKING state: Fast pacing left/right.

        The agent paces back and forth at 3x normal speed.
        """
        pace_speed = self.move_speed * 3  # 3x faster
        distance = self.position.distance_to(self.target_position)

        # BUG FIX: Check distance > 1 before normalizing
        if distance > 1.0:
            direction = (self.target_position - self.position).normalize()
            move_distance = pace_speed * dt
            if move_distance > distance:
                self.position = self.target_position.copy()
            else:
                self.position += direction * move_distance
        else:
            # Reached end, flip direction
            pace_distance = 64  # 2 tiles
            self.pace_direction *= -1
            self.target_position.x = self.position.x + (pace_distance * self.pace_direction)

    def _update_talking(self, dt: float) -> None:
        """
        TALKING state: Gentle bob animation.

        The agent bobs up and down smoothly while talking.
        BUG FIX: Uses base_y + sin() instead of += to prevent drift.
        """
        bob_speed = 4.0  # radians per second (full cycle ~1.57 seconds)
        bob_amplitude = 2.0  # pixels

        # Increment bob offset
        self.bob_offset += bob_speed * dt

        # BUG FIX: Use base_y + sin(), NOT += with dt
        # This prevents cumulative drift
        self.position.y = self.bob_base_y + math.sin(self.bob_offset) * bob_amplitude

    def _update_error(self, dt: float) -> None:
        """
        ERROR state: Shake for 2 seconds, then return to IDLE.

        BUG FIX: Stores base position to prevent drift from shake.
        """
        if self.state_timer < 2.0:
            # BUG FIX: Shake relative to base position to prevent drift
            shake_amount = 3 * math.sin(self.state_timer * 20)
            self.position.x = self.error_base_pos.x + shake_amount
            self.position.y = self.error_base_pos.y
        else:
            # Return to idle after 2 seconds
            self.set_state(AgentState.IDLE)

    def _pick_random_target(self) -> None:
        """
        Pick random position within 2 tiles, clamped to world bounds.

        BUG FIX: Clamps target to world bounds to prevent escaping.
        """
        # Random offset within 2 tiles (64px)
        offset_x = random.randint(-64, 64)
        offset_y = random.randint(-64, 64)

        new_target = self.position + pygame.math.Vector2(offset_x, offset_y)

        # BUG FIX: Clamp to world bounds with margin to keep agent visible
        margin = 20  # Keep agent away from exact edges
        new_target.x = max(self.world_bounds['min_x'] + margin,
                          min(self.world_bounds['max_x'] - margin, new_target.x))
        new_target.y = max(self.world_bounds['min_y'] + margin,
                          min(self.world_bounds['max_y'] - margin, new_target.y))

        self.target_position = new_target

    def set_state(self, new_state: AgentState) -> None:
        """
        Transition to a new state.

        BUG FIX: Always resets state_timer to 0.0.

        Args:
            new_state: The state to transition to
        """
        if new_state != self.state:
            logger.debug(f"{self.name} state: {self.state.value} -> {new_state.value}")

        self.state = new_state
        self.state_timer = 0.0  # BUG FIX: Always reset timer

        # State-specific initialization
        if new_state == AgentState.THINKING:
            # Start pacing to the right
            pace_distance = 64
            self.pace_direction = 1
            self.target_position = self.position + pygame.math.Vector2(pace_distance, 0)

        elif new_state == AgentState.TALKING:
            # BUG FIX: Store base position for bob animation
            self.bob_base_y = self.position.y
            self.bob_offset = 0.0

        elif new_state == AgentState.ERROR:
            # BUG FIX: Store base position for shake animation
            self.error_base_pos = self.position.copy()

        elif new_state == AgentState.IDLE:
            # Pick new random target
            self._pick_random_target()

    def render(self, surface: pygame.Surface, camera_offset: pygame.math.Vector2) -> None:
        """
        Render the agent sprite.

        Args:
            surface: pygame Surface to render onto
            camera_offset: Current camera position offset
        """
        # Convert world position to screen position
        screen_pos = self.position - camera_offset

        # Draw sprite
        sprite_rect = self.image.get_rect(center=(int(screen_pos.x), int(screen_pos.y)))
        surface.blit(self.image, sprite_rect)

        # Draw selection highlight (2px white border)
        if self.selected:
            pygame.draw.rect(
                surface,
                pygame.Color("#E8E8E8"),  # Off-white from config colors
                sprite_rect.inflate(4, 4),
                2  # border width
            )

        # Draw error outline (2px red border)
        if self.state == AgentState.ERROR:
            pygame.draw.rect(
                surface,
                pygame.Color("#E57373"),  # Error red from config colors
                sprite_rect.inflate(4, 4),
                2
            )

    def handle_click(self, mouse_pos: Tuple[int, int],
                     camera_offset: pygame.math.Vector2) -> bool:
        """
        Check if this agent was clicked.

        Args:
            mouse_pos: Mouse position in screen coordinates
            camera_offset: Current camera offset

        Returns:
            True if agent was clicked, False otherwise
        """
        # Convert world position to screen position
        screen_pos = self.position - camera_offset

        # Create rect in screen space
        click_rect = pygame.Rect(
            screen_pos.x - self.size[0] // 2,
            screen_pos.y - self.size[1] // 2,
            self.size[0],
            self.size[1]
        )

        return click_rect.collidepoint(mouse_pos)
