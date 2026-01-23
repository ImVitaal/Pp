"""Agent entities for PixelPrompt.

Defines the Agent class with state machine and animations.
"""

import pygame
import logging
import math
import random
import os
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent behavior states."""
    IDLE = "idle"          # Random walks every 3-5s
    THINKING = "thinking"  # Paces quickly
    TALKING = "talking"    # Stands still, bobs
    ERROR = "error"        # Red outline, shows error bubble


class Agent(pygame.sprite.Sprite):
    """AI agent sprite with state machine and animations."""

    def __init__(self, config: Dict, world):
        """
        Initialize agent from configuration.

        Args:
            config: Agent configuration dict
            world: World instance for collision/movement
        """
        super().__init__()

        self.id = config['id']
        self.name = config['name']
        self.provider_name = config['provider']
        self.model = config['model']

        # State management
        self.state = AgentState.IDLE
        self.state_timer = 0.0

        # Position and movement
        spawn_pos = config.get('spawn_position', [640, 360])
        self.position = pygame.math.Vector2(spawn_pos)
        self.target_position = self.position.copy()
        self.move_speed = 50.0  # pixels/second

        # Visuals
        color_hex = config.get('color_hex', '#7DCFB6')
        self.color = pygame.Color(color_hex)
        self.size = (20, 40)  # width, height
        self.selected = False

        # Animation
        self.bob_offset = 0.0
        self.bob_direction = 1

        # Communication
        self.speech_bubble: Optional = None
        self.conversation_history: List[Dict] = []
        self.max_history = config.get('max_history', 10)

        # Add system prompt to history if present
        system_prompt = config.get('system_prompt')
        if system_prompt:
            self.conversation_history.append({
                'role': 'system',
                'content': system_prompt
            })

        # Create sprite surface
        self._create_sprite()

        # World reference
        self.world = world

        logger.info(f"Agent initialized: {self.name} ({self.provider_name}/{self.model})")

    def _create_sprite(self) -> None:
        """Create placeholder sprite or load from file."""
        sprite_path = f"assets/sprites/{self.id}.png"

        if os.path.exists(sprite_path):
            try:
                self.image = pygame.image.load(sprite_path)
                logger.info(f"Loaded sprite from {sprite_path}")
            except Exception as e:
                logger.warning(f"Failed to load sprite {sprite_path}: {e}, using fallback")
                self._create_fallback_sprite()
        else:
            self._create_fallback_sprite()

        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def _create_fallback_sprite(self) -> None:
        """Create a simple colored rectangle sprite."""
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
        # Draw rounded rectangle
        pygame.draw.rect(
            self.image,
            self.color,
            (0, 0, self.size[0], self.size[1]),
            border_radius=4
        )
        # Add simple eyes
        eye_color = pygame.Color("#2E2E3A")
        pygame.draw.circle(self.image, eye_color, (6, 12), 2)
        pygame.draw.circle(self.image, eye_color, (14, 12), 2)

    def update(self, dt: float) -> None:
        """
        Update agent state and animations.

        Args:
            dt: Delta time since last frame (seconds)
        """
        self.state_timer += dt

        # State machine
        if self.state == AgentState.IDLE:
            self._update_idle(dt)
        elif self.state == AgentState.THINKING:
            self._update_thinking(dt)
        elif self.state == AgentState.TALKING:
            self._update_talking(dt)
        elif self.state == AgentState.ERROR:
            self._update_error(dt)

        # Update sprite position
        self.rect.center = self.position

        # Update speech bubble if present
        if self.speech_bubble:
            self.speech_bubble.update(dt)
            if self.speech_bubble.is_finished():
                self.speech_bubble = None
                # Return to idle after talking
                if self.state == AgentState.TALKING:
                    self.set_state(AgentState.IDLE)

    def _update_idle(self, dt: float) -> None:
        """Idle state: random walks."""
        # Move toward target
        if self.position.distance_to(self.target_position) > 1:
            direction = (self.target_position - self.position).normalize()
            self.position += direction * self.move_speed * dt

        # Pick new target every 3-5 seconds
        elif self.state_timer > random.uniform(3.0, 5.0):
            self._pick_random_target()
            self.state_timer = 0.0

    def _update_thinking(self, dt: float) -> None:
        """Thinking state: pace back and forth."""
        pace_speed = self.move_speed * 3
        pace_distance = 64  # 2 tiles

        # Move toward target
        if self.position.distance_to(self.target_position) > 1:
            direction = (self.target_position - self.position).normalize()
            self.position += direction * pace_speed * dt
        else:
            # Flip direction
            if self.target_position.x > self.position.x:
                self.target_position.x = self.position.x - pace_distance
            else:
                self.target_position.x = self.position.x + pace_distance

    def _update_talking(self, dt: float) -> None:
        """Talking state: bob up and down."""
        bob_speed = 0.5  # Hz
        bob_amplitude = 2  # pixels

        self.bob_offset += self.bob_direction * bob_speed * dt * math.pi
        # Apply subtle bob (this modifies position slightly)

    def _update_error(self, dt: float) -> None:
        """Error state: shake horizontally."""
        if self.state_timer < 2.0:
            # Subtle shake
            shake_amount = 1 * math.sin(self.state_timer * 20)
            # Store original position to shake around
            if not hasattr(self, '_error_origin'):
                self._error_origin = self.position.copy()
            self.position.x = self._error_origin.x + shake_amount
        else:
            # Return to idle
            if hasattr(self, '_error_origin'):
                delattr(self, '_error_origin')
            self.set_state(AgentState.IDLE)

    def _pick_random_target(self) -> None:
        """Pick a random position within 2 tiles."""
        offset_x = random.randint(-64, 64)
        offset_y = random.randint(-64, 64)
        new_target = self.position + pygame.math.Vector2(offset_x, offset_y)

        # Clamp to world bounds
        new_target.x = max(32, min(self.world.width - 32, new_target.x))
        new_target.y = max(32, min(self.world.height - 32, new_target.y))

        self.target_position = new_target

    def set_state(self, new_state: AgentState) -> None:
        """
        Change agent state.

        Args:
            new_state: Target state
        """
        self.state = new_state
        self.state_timer = 0.0

        if new_state == AgentState.THINKING:
            # Start pacing
            self.target_position = self.position + pygame.math.Vector2(64, 0)

        logger.debug(f"Agent {self.name} -> {new_state.value}")

    def handle_click(self, mouse_pos: Tuple[int, int],
                    camera_offset: pygame.math.Vector2) -> bool:
        """
        Check if click intersects sprite.

        Args:
            mouse_pos: Mouse position in screen coordinates
            camera_offset: Camera offset for world-to-screen conversion

        Returns:
            bool: True if click hit this agent
        """
        screen_pos = self.position - camera_offset
        click_rect = pygame.Rect(
            screen_pos.x - self.size[0] // 2,
            screen_pos.y - self.size[1] // 2,
            self.size[0],
            self.size[1]
        )
        return click_rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface,
              camera_offset: pygame.math.Vector2) -> None:
        """
        Render agent sprite and bubble.

        Args:
            surface: Surface to draw on
            camera_offset: Camera offset for positioning
        """
        screen_pos = self.position - camera_offset

        # Draw sprite
        sprite_rect = self.image.get_rect(center=screen_pos)
        surface.blit(self.image, sprite_rect)

        # Draw selection highlight
        if self.selected:
            pygame.draw.rect(
                surface,
                pygame.Color("#E8E8E8"),
                sprite_rect.inflate(4, 4),
                2  # 2px border
            )

        # Draw error outline
        if self.state == AgentState.ERROR:
            pygame.draw.rect(
                surface,
                pygame.Color("#E57373"),
                sprite_rect.inflate(4, 4),
                2
            )

        # Draw name tag below agent
        font = pygame.font.Font(None, 16)
        name_surface = font.render(self.name, True, pygame.Color("#E8E8E8"))
        name_rect = name_surface.get_rect(center=(screen_pos[0], screen_pos[1] + 30))
        surface.blit(name_surface, name_rect)

        # Draw speech bubble
        if self.speech_bubble:
            bubble_pos = (screen_pos[0], screen_pos[1] - 50)
            self.speech_bubble.render(surface, bubble_pos)
