"""Game engine for PixelPrompt.

Manages the main game loop, state, and rendering.
"""

import pygame
import logging
from enum import Enum
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Game state enumeration."""
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"


class GameEngine:
    """Main game engine managing pygame loop and state."""

    def __init__(self, config: Dict):
        """
        Initialize pygame and game systems.

        Args:
            config: Configuration dictionary from config_manager
        """
        pygame.init()

        self.config = config
        window_cfg = config['window']

        # Create window
        flags = pygame.RESIZABLE if window_cfg.get('resizable', True) else 0
        self.screen = pygame.display.set_mode(
            (window_cfg['width'], window_cfg['height']),
            flags
        )
        pygame.display.set_caption("PixelPrompt")

        # Clock and FPS
        self.clock = pygame.time.Clock()
        self.fps_target = window_cfg.get('fps_target', 60)
        self.running = True
        self.state = GameState.RUNNING

        # Camera system
        self.camera_offset = pygame.math.Vector2(0, 0)

        # Import here to avoid circular dependency
        from src.world import World
        self.world = World(config)

        # Agents (will be populated)
        self.agents: List = []

        # LLM providers and client (will be initialized later)
        self.llm_providers: Dict = {}
        self.llm_client = None

        # UI manager (will be initialized in Phase 4)
        self.ui_manager = None

        # Selected agent
        self.selected_agent = None

        logger.info("Game engine initialized")

    def run(self) -> None:
        """Main game loop at target FPS."""
        logger.info("Starting game loop")

        while self.running:
            # Calculate delta time
            dt = self.clock.tick(self.fps_target) / 1000.0

            # Process events
            self.handle_events()

            # Update game state
            if self.state == GameState.RUNNING:
                self.update(dt)

            # Render frame
            self.render()

        logger.info("Game loop ended")

    def handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_agent_click(event.pos)

            elif event.type == pygame.VIDEORESIZE:
                if self.ui_manager:
                    self.ui_manager.resize(event.size)

            # Pass events to UI manager if it exists
            if self.ui_manager:
                message = self.ui_manager.process_events(event)
                if message:
                    self._send_message_to_agent(message)

    def update(self, dt: float) -> None:
        """
        Update game state.

        Args:
            dt: Delta time since last frame (seconds)
        """
        # Update camera
        self.update_camera(dt)

        # Update agents
        for agent in self.agents:
            agent.update(dt)

        # Update UI
        if self.ui_manager:
            self.ui_manager.update(dt)

        # Process LLM responses if client exists
        if self.llm_client:
            self._process_llm_responses()

    def update_camera(self, dt: float) -> None:
        """
        Handle WASD camera movement.

        Args:
            dt: Delta time (unused, movement is frame-based)
        """
        keys = pygame.key.get_pressed()
        speed = self.config['camera']['pan_speed']
        bounds = self.config['camera']['bounds']

        if keys[pygame.K_w]:
            self.camera_offset.y = max(
                bounds['min_y'],
                self.camera_offset.y - speed
            )
        if keys[pygame.K_s]:
            self.camera_offset.y = min(
                bounds['max_y'] - self.screen.get_height(),
                self.camera_offset.y + speed
            )
        if keys[pygame.K_a]:
            self.camera_offset.x = max(
                bounds['min_x'],
                self.camera_offset.x - speed
            )
        if keys[pygame.K_d]:
            self.camera_offset.x = min(
                bounds['max_x'] - self.screen.get_width(),
                self.camera_offset.x + speed
            )

    def render(self) -> None:
        """Render frame."""
        # Clear screen with background color
        bg_color = pygame.Color("#2E2E3A")
        self.screen.fill(bg_color)

        # Render world
        self.world.render(self.screen, self.camera_offset)

        # Render agents
        for agent in self.agents:
            agent.render(self.screen, self.camera_offset)

        # Render UI
        if self.ui_manager:
            self.ui_manager.render(self.screen)

        # Update display
        pygame.display.flip()

    def _handle_agent_click(self, mouse_pos: Tuple[int, int]) -> None:
        """
        Check if any agent was clicked.

        Args:
            mouse_pos: Mouse position in screen coordinates
        """
        for agent in self.agents:
            if agent.handle_click(mouse_pos, self.camera_offset):
                # Deselect all other agents
                for a in self.agents:
                    a.selected = False
                # Select this one
                agent.selected = True
                self.selected_agent = agent
                logger.info(f"Selected agent: {agent.name}")
                break

    def _send_message_to_agent(self, message: str) -> None:
        """
        Send message to selected agent.

        Args:
            message: User message text
        """
        if self.selected_agent is None:
            # Auto-select first agent if none selected
            if self.agents:
                self.selected_agent = self.agents[0]
                self.selected_agent.selected = True
            else:
                logger.warning("No agents available to send message to")
                return

        agent = self.selected_agent

        # Add to history
        agent.conversation_history.append({
            'role': 'user',
            'content': message
        })

        # Trim history to max
        if len(agent.conversation_history) > agent.max_history * 2:
            # Keep system prompt + recent messages
            system_msg = next(
                (m for m in agent.conversation_history if m['role'] == 'system'),
                None
            )
            recent = agent.conversation_history[-(agent.max_history * 2):]
            agent.conversation_history = ([system_msg] if system_msg else []) + recent

        # Import here to avoid circular dependency
        from src.entities import AgentState

        # Set thinking state
        agent.set_state(AgentState.THINKING)

        # Queue LLM request
        if self.llm_client:
            self.llm_client.send_message(
                agent_id=agent.id,
                provider_name=agent.provider_name,
                model=agent.model,
                message=message,
                history=agent.conversation_history
            )
            logger.info(f"Sent message to {agent.name}")
        else:
            logger.error("LLM client not initialized")

    def _process_llm_responses(self) -> None:
        """Check for and handle LLM responses from queue."""
        # Import here to avoid circular dependency
        from src.entities import AgentState
        from src.ui import SpeechBubble

        while True:
            response = self.llm_client.get_response()
            if response is None:
                break

            # Find the agent this response is for
            agent = self._get_agent_by_id(response['agent_id'])
            if agent is None:
                logger.warning(f"Received response for unknown agent: {response['agent_id']}")
                continue

            if response['status'] == 'success':
                # Create speech bubble
                agent.speech_bubble = SpeechBubble(
                    text=response['text'],
                    max_width=self.config['ui']['bubble_max_width']
                )
                agent.set_state(AgentState.TALKING)

                # Update conversation history
                agent.conversation_history.append({
                    'role': 'assistant',
                    'content': response['text']
                })

                logger.info(f"Agent {agent.name} responded: {response['text'][:50]}...")

            elif response['status'] == 'error':
                # Show error in bubble
                error_msg = self._format_error(response['error'])
                agent.speech_bubble = SpeechBubble(
                    text=error_msg,
                    max_width=self.config['ui']['bubble_max_width'],
                    is_error=True
                )
                agent.set_state(AgentState.ERROR)

                logger.error(f"Agent {agent.name} error: {response['error']}")

    def _get_agent_by_id(self, agent_id: str) -> Optional:
        """
        Find agent by ID.

        Args:
            agent_id: Agent ID to search for

        Returns:
            Agent instance or None if not found
        """
        for agent in self.agents:
            if agent.id == agent_id:
                return agent
        return None

    def _format_error(self, error: str) -> str:
        """
        Convert technical errors to user-friendly messages.

        Args:
            error: Error message

        Returns:
            User-friendly error message
        """
        error_lower = error.lower()

        if 'connectionerror' in error_lower or 'cannot reach' in error_lower:
            return "Can't reach LLM service"
        elif 'timeouterror' in error_lower or 'timed out' in error_lower:
            return "Request timed out"
        elif '404' in error or 'not found' in error_lower:
            return "Model not found"
        elif 'api key' in error_lower or '401' in error or '403' in error:
            return "Invalid API key"
        else:
            # Truncate long error messages
            return f"Error: {error[:50]}"

    def cleanup(self) -> None:
        """Clean shutdown."""
        logger.info("Cleaning up...")

        if self.llm_client:
            self.llm_client.stop()

        pygame.quit()
        logger.info("Cleanup complete")
