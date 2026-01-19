"""
Gemini provider stub - Phase 6 implementation.

This file is a placeholder for the Google Gemini API provider.
Implementation is planned for Phase 6.

To implement:
1. pip install google-generativeai>=0.8.0
2. Implement the GeminiProvider class below
3. Remove the NotImplementedError raises

See PRD.md Section 5.2 for implementation details.
"""

from typing import Generator, List, Dict
import logging

from . import BaseLLMProvider

logger = logging.getLogger("pixelprompt.llm.gemini")


class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini cloud API provider.

    NOT YET IMPLEMENTED - Phase 6 feature.
    """

    def __init__(self, api_key: str):
        """
        Initialize Gemini provider.

        Args:
            api_key: Google AI Studio API key
        """
        raise NotImplementedError(
            "GeminiProvider is not yet implemented. "
            "This is planned for Phase 6. "
            "For now, please use the 'ollama' provider with a local model. "
            "See: https://ai.google.dev/gemini-api/docs for Gemini API documentation."
        )

    @property
    def name(self) -> str:
        """Provider display name."""
        return "Google Gemini"

    def send_message(
        self,
        messages: List[Dict[str, str]],
        model: str,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream responses from Gemini API - NOT IMPLEMENTED."""
        raise NotImplementedError("GeminiProvider.send_message not implemented")

    def is_available(self) -> bool:
        """Check if Gemini is available - NOT IMPLEMENTED."""
        return False

    def list_models(self) -> List[str]:
        """Return supported Gemini models."""
        return [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]
