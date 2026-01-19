"""
Claude provider stub - Phase 6 implementation.

This file is a placeholder for the Anthropic Claude API provider.
Implementation is planned for Phase 6.

To implement:
1. pip install anthropic>=0.39.0
2. Implement the ClaudeProvider class below
3. Remove the NotImplementedError raises

See PRD.md Section 5.2 for implementation details.
"""

from typing import Generator, List, Dict
import logging

from . import BaseLLMProvider

logger = logging.getLogger("pixelprompt.llm.claude")


class ClaudeProvider(BaseLLMProvider):
    """
    Anthropic Claude cloud API provider.

    NOT YET IMPLEMENTED - Phase 6 feature.
    """

    def __init__(self, api_key: str):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
        """
        raise NotImplementedError(
            "ClaudeProvider is not yet implemented. "
            "This is planned for Phase 6. "
            "For now, please use the 'ollama' provider with a local model. "
            "See: https://docs.anthropic.com/ for Claude API documentation."
        )

    @property
    def name(self) -> str:
        """Provider display name."""
        return "Anthropic Claude"

    def send_message(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream responses from Claude API - NOT IMPLEMENTED."""
        raise NotImplementedError("ClaudeProvider.send_message not implemented")

    def is_available(self) -> bool:
        """Check if Claude is available - NOT IMPLEMENTED."""
        return False

    def list_models(self) -> List[str]:
        """Return supported Claude models."""
        return [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-5-20251101",
            "claude-haiku-4-5-20251001",
        ]
