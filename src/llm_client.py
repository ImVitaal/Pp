"""Thread-safe LLM client for PixelPrompt.

Manages non-blocking LLM calls using request/response queues.
"""

import threading
import logging
from queue import Queue, Empty
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Thread-safe LLM client supporting multiple providers.

    Manages request/response queues and background worker thread
    to prevent blocking the main game loop.
    """

    def __init__(self, providers: Dict):
        """
        Initialize client with provider instances.

        Args:
            providers: Dict mapping provider names to instances
        """
        self.providers = providers

        self.request_queue: Queue = Queue()
        self.response_queue: Queue = Queue()

        self.worker_thread: Optional[threading.Thread] = None
        self.running = False

        logger.info("LLM client initialized")

    def start(self) -> None:
        """Launch background worker thread."""
        if self.worker_thread is not None:
            logger.warning("Worker thread already running")
            return

        self.running = True
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            daemon=True,
            name="LLMWorker"
        )
        self.worker_thread.start()
        logger.info("LLM worker thread started")

    def stop(self) -> None:
        """Stop worker thread gracefully."""
        logger.info("Stopping LLM worker thread...")
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            self.worker_thread = None
        logger.info("LLM worker thread stopped")

    def send_message(self,
                    agent_id: str,
                    provider_name: str,
                    model: str,
                    message: str,
                    history: List[Dict]) -> None:
        """
        Queue a message for LLM processing (non-blocking).

        Args:
            agent_id: Agent requesting the response
            provider_name: Which provider to use ("ollama", "gemini", "claude")
            model: Model identifier
            message: User message text
            history: Conversation history
        """
        self.request_queue.put({
            'agent_id': agent_id,
            'provider': provider_name,
            'model': model,
            'message': message,
            'history': history.copy()  # Copy to avoid threading issues
        })
        logger.debug(f"Queued message for {agent_id} via {provider_name}")

    def get_response(self) -> Optional[Dict]:
        """
        Check for completed responses (non-blocking).

        Returns:
            Dict with 'agent_id', 'status' ('success'/'error'),
            'text' or 'error' field, or None if no response ready
        """
        try:
            return self.response_queue.get_nowait()
        except Empty:
            return None

    def _worker_loop(self) -> None:
        """Background thread: processes queue and calls LLM APIs."""
        logger.info("Worker loop started")

        while self.running:
            try:
                # Block for up to 1 second waiting for requests
                request = self.request_queue.get(timeout=1.0)
            except Empty:
                continue

            try:
                logger.info(f"Processing request for agent {request['agent_id']}")
                response_text = self._call_llm(request)
                self.response_queue.put({
                    'agent_id': request['agent_id'],
                    'status': 'success',
                    'text': response_text
                })
                logger.info(f"Response ready for agent {request['agent_id']}")
            except Exception as e:
                logger.error(f"LLM call failed: {e}")
                self.response_queue.put({
                    'agent_id': request['agent_id'],
                    'status': 'error',
                    'error': str(e)
                })

        logger.info("Worker loop stopped")

    def _call_llm(self, request: Dict) -> str:
        """
        Execute LLM call with streaming.

        Args:
            request: Request dict with provider, model, message, history

        Returns:
            str: Complete response text

        Raises:
            ValueError: Invalid provider
            ConnectionError: Provider unreachable
            TimeoutError: Request timed out
        """
        provider_name = request['provider']

        if provider_name not in self.providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider = self.providers[provider_name]

        # Check if provider is available
        if not provider.is_available():
            raise ConnectionError(f"{provider.name} is not available")

        # Build message list
        messages = request['history'].copy()
        messages.append({
            'role': 'user',
            'content': request['message']
        })

        # Stream response and accumulate
        response_chunks = []
        try:
            for chunk in provider.send_message(messages, request['model']):
                response_chunks.append(chunk)
        except Exception as e:
            logger.error(f"Error during streaming: {e}")
            raise

        full_response = ''.join(response_chunks)

        if not full_response:
            raise ValueError("Empty response from provider")

        return full_response
