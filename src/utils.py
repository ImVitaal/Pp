"""Utility functions and logging setup for PixelPrompt."""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, uses logs/pixelprompt.log
        
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Use default log file if not specified
    if log_file is None:
        timestamp = datetime.now().strftime("%Y%m%d")
        log_file = log_dir / f"pixelprompt_{timestamp}.log"
    
    # Create logger
    logger = logging.getLogger("pixelprompt")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Console handler with color coding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)8s | %(name)s | %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler with detailed formatting
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)8s | %(name)s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")
    return logger


class ColoredFormatter(logging.Formatter):
    """Custom formatter with color coding for console output."""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def show_error_dialog(message: str, title: str = "Error") -> None:
    """
    Display a simple error message (console-based for now).
    
    In Phase 4+, this will use pygame_gui for graphical dialogs.
    
    Args:
        message: Error message to display
        title: Dialog title
    """
    logger = logging.getLogger("pixelprompt")
    logger.error(f"{title}: {message}")
    
    # Simple console output
    print(f"\n{'='*60}")
    print(f"❌ {title}")
    print(f"{'='*60}")
    print(f"{message}")
    print(f"{'='*60}\n")


def show_warning_dialog(message: str, title: str = "Warning") -> None:
    """
    Display a warning message.
    
    Args:
        message: Warning message to display
        title: Dialog title
    """
    logger = logging.getLogger("pixelprompt")
    logger.warning(f"{title}: {message}")
    
    print(f"\n{'='*60}")
    print(f"⚠️  {title}")
    print(f"{'='*60}")
    print(f"{message}")
    print(f"{'='*60}\n")


def show_success_dialog(message: str, title: str = "Success") -> None:
    """
    Display a success message.
    
    Args:
        message: Success message to display
        title: Dialog title
    """
    logger = logging.getLogger("pixelprompt")
    logger.info(f"{title}: {message}")
    
    print(f"\n{'='*60}")
    print(f"✅ {title}")
    print(f"{'='*60}")
    print(f"{message}")
    print(f"{'='*60}\n")


def format_error_message(error: Exception) -> str:
    """
    Convert technical errors to user-friendly messages.
    
    Args:
        error: Exception object
        
    Returns:
        User-friendly error message
    """
    error_str = str(error).lower()
    error_type = type(error).__name__
    
    # Connection errors
    if 'connection' in error_str or error_type == 'ConnectionError':
        return "🔌 Can't reach the service. Is it running?"
    
    # Timeout errors
    if 'timeout' in error_str or error_type == 'TimeoutError':
        return "⏱️ Request timed out. Try again?"
    
    # File not found
    if error_type == 'FileNotFoundError':
        return f"📁 File not found: {error}"
    
    # Permission errors
    if error_type == 'PermissionError':
        return f"🔒 Permission denied: {error}"
    
    # JSON errors
    if 'json' in error_str or 'parse' in error_str:
        return "⚠️ Invalid configuration format"
    
    # Generic error
    return f"⚠️ Error: {str(error)[:100]}"
