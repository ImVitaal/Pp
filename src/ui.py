"""UI components for PixelPrompt.

Includes chat input, speech bubbles, and UI management.
"""

import pygame
import pygame_gui
import logging
from typing import Optional, Tuple, List

logger = logging.getLogger(__name__)


class UIManager:
    """Manages all pygame_gui elements."""

    def __init__(self, screen_size: Tuple[int, int], config: dict):
        """
        Initialize UI manager.

        Args:
            screen_size: (width, height) of game window
            config: UI configuration dict
        """
        self.manager = pygame_gui.UIManager(screen_size)
        self.config = config

        # UI elements
        self.text_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        self.send_button: Optional[pygame_gui.elements.UIButton] = None

        self._setup_chat_bar(screen_size)

        logger.info("UI manager initialized")

    def _setup_chat_bar(self, screen_size: Tuple[int, int]) -> None:
        """Create bottom-anchored input bar."""
        width, height = screen_size
        bar_height = self.config.get('input_box_height', 50)

        input_width = int(width * 0.75)
        button_width = int(width * 0.20)
        margin = 10

        # Text input
        self.text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(
                margin,
                height - bar_height - margin,
                input_width,
                bar_height
            ),
            manager=self.manager,
            placeholder_text="Type message..."
        )

        # Send button
        self.send_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(
                input_width + margin * 2,
                height - bar_height - margin,
                button_width,
                bar_height
            ),
            text="Send",
            manager=self.manager
        )

    def process_events(self, event: pygame.event.Event) -> Optional[str]:
        """
        Process UI events.

        Args:
            event: Pygame event

        Returns:
            str: Message text if send triggered, else None
        """
        self.manager.process_events(event)

        # Check for send triggers
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.send_button:
                return self._get_and_clear_input()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.text_input.is_focused:
                    return self._get_and_clear_input()

        return None

    def _get_and_clear_input(self) -> Optional[str]:
        """Get text from input and clear it."""
        text = self.text_input.get_text().strip()
        if text:
            self.text_input.set_text("")
            logger.debug(f"User input: {text}")
            return text
        return None

    def update(self, dt: float) -> None:
        """Update UI manager."""
        self.manager.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        """Draw UI elements."""
        self.manager.draw_ui(surface)

    def resize(self, new_size: Tuple[int, int]) -> None:
        """Handle window resize."""
        self.manager.set_window_resolution(new_size)
        # Kill old UI elements
        if self.text_input:
            self.text_input.kill()
        if self.send_button:
            self.send_button.kill()
        # Recreate chat bar with new dimensions
        self._setup_chat_bar(new_size)


class SpeechBubble:
    """Animated speech bubble for agent responses."""

    def __init__(self, text: str, max_width: int, is_error: bool = False):
        """
        Create speech bubble.

        Args:
            text: Full text to display
            max_width: Maximum bubble width in pixels
            is_error: If True, use error styling
        """
        self.full_text = text
        self.displayed_text = ""
        self.typewriter_index = 0
        self.typewriter_timer = 0.0

        self.max_width = max_width
        self.padding = 10

        # Colors
        if is_error:
            self.bg_color = pygame.Color("#E57373")  # Soft red
            self.text_color = pygame.Color("#FFFFFF")
        else:
            self.bg_color = pygame.Color("#FFFFFF")
            self.text_color = pygame.Color("#2E2E3A")

        # Font
        self.font = pygame.font.Font(None, 20)

        # Auto-dismiss timer
        self.lifetime = 10.0  # seconds
        self.age = 0.0

        logger.debug(f"Speech bubble created: {text[:30]}...")

    def update(self, dt: float) -> None:
        """
        Update typewriter effect and lifetime.

        Args:
            dt: Delta time (seconds)
        """
        self.age += dt

        # Typewriter effect
        if self.typewriter_index < len(self.full_text):
            self.typewriter_timer += dt

            # Reveal characters at configured rate
            delay = 0.03  # 30ms per character
            chars_to_reveal = int(self.typewriter_timer / delay)

            if chars_to_reveal > 0:
                self.typewriter_index = min(
                    self.typewriter_index + chars_to_reveal,
                    len(self.full_text)
                )
                self.displayed_text = self.full_text[:self.typewriter_index]
                self.typewriter_timer = 0.0
        else:
            # Fully displayed
            self.displayed_text = self.full_text

    def is_finished(self) -> bool:
        """Check if bubble should disappear."""
        return self.age >= self.lifetime

    def render(self, surface: pygame.Surface, position: Tuple[int, int]) -> None:
        """
        Draw bubble above agent.

        Args:
            surface: Surface to draw on
            position: (x, y) position (tip of bubble points here)
        """
        if not self.displayed_text:
            return

        # Word wrap text
        wrapped_lines = self._wrap_text(self.displayed_text)

        # Calculate bubble size
        line_height = self.font.get_linesize()
        text_height = len(wrapped_lines) * line_height
        text_width = max(
            self.font.size(line)[0] for line in wrapped_lines
        ) if wrapped_lines else 0

        bubble_width = min(text_width + self.padding * 2, self.max_width)
        bubble_height = text_height + self.padding * 2

        # Position bubble above agent (centered)
        bubble_x = position[0] - bubble_width // 2
        bubble_y = position[1] - bubble_height - 10  # 10px gap

        # Clamp to screen bounds
        screen_width, screen_height = surface.get_size()
        bubble_x = max(5, min(bubble_x, screen_width - bubble_width - 5))
        bubble_y = max(5, bubble_y)

        # Draw rounded rectangle
        bubble_rect = pygame.Rect(
            bubble_x, bubble_y,
            bubble_width, bubble_height
        )
        pygame.draw.rect(surface, self.bg_color, bubble_rect, border_radius=8)
        pygame.draw.rect(
            surface,
            pygame.Color("#2E2E3A"),
            bubble_rect,
            2,  # 2px border
            border_radius=8
        )

        # Draw pointer triangle (only if not at screen top)
        if bubble_y > 20:
            tip_x = position[0]
            tip_y = position[1] - 10
            # Clamp tip to bubble width
            tip_x = max(bubble_x + 10, min(tip_x, bubble_x + bubble_width - 10))

            pygame.draw.polygon(
                surface,
                self.bg_color,
                [
                    (tip_x, tip_y),
                    (tip_x - 8, tip_y - 10),
                    (tip_x + 8, tip_y - 10)
                ]
            )

        # Draw text
        y_offset = bubble_y + self.padding
        for line in wrapped_lines:
            text_surface = self.font.render(line, True, self.text_color)
            surface.blit(
                text_surface,
                (bubble_x + self.padding, y_offset)
            )
            y_offset += line_height

    def _wrap_text(self, text: str) -> List[str]:
        """
        Word-wrap text to fit max width.

        Args:
            text: Text to wrap

        Returns:
            List of wrapped lines (max 5 lines)
        """
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if self.font.size(test_line)[0] <= self.max_width - self.padding * 2:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        # Truncate to 5 lines
        if len(lines) > 5:
            lines = lines[:5]
            lines[-1] += "..."

        return lines
