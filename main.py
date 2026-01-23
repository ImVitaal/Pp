#!/usr/bin/env python3
"""PixelPrompt - AI Agent Visualization Engine

Entry point for the application.
"""

import sys
import argparse
import logging
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils import setup_logging, show_error_dialog, show_success_dialog, show_warning_dialog
from src.config_manager import load_config, check_provider_credentials
from src.llm_providers import create_provider

logger = None  # Will be initialized after argument parsing


def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="PixelPrompt - Visualize AI models as pixel-art agents",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run environment validation checks and exit"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    
    return parser.parse_args()


def validate_environment() -> dict:
    """
    Run comprehensive environment validation.
    
    Returns:
        Dict with validation results for each check
    """
    results = {
        'python_version': False,
        'pygame_ce': False,
        'pygame_gui': False,
        'requests': False,
        'dotenv': False,
        'ollama_server': False,
        'config_valid': False
    }
    
    # Check Python version (3.10+)
    if sys.version_info >= (3, 10):
        results['python_version'] = True
        logger.info(f"[OK] Python version: {sys.version.split()[0]}")
    else:
        logger.error(f"[FAIL] Python version {sys.version.split()[0]} < 3.10")
    
    # Check pygame-ce
    try:
        import pygame
        results['pygame_ce'] = True
        logger.info(f"[OK] pygame-ce installed: {pygame.version.ver}")
    except ImportError:
        logger.error("[FAIL] pygame-ce not installed")
    
    # Check pygame_gui
    try:
        import pygame_gui
        results['pygame_gui'] = True
        logger.info(f"[OK] pygame_gui installed")
    except ImportError:
        logger.error("[FAIL] pygame_gui not installed")
    
    # Check requests
    try:
        import requests
        results['requests'] = True
        logger.info(f"[OK] requests installed: {requests.__version__}")
    except ImportError:
        logger.error("[FAIL] requests not installed")
    
    # Check python-dotenv
    try:
        import dotenv
        results['dotenv'] = True
        logger.info(f"[OK] python-dotenv installed")
    except ImportError:
        logger.error("[FAIL] python-dotenv not installed")
    
    # Try to load config
    try:
        config = load_config("config.json")
        results['config_valid'] = True
        logger.info("[OK] Configuration loaded successfully")
        
        # Check Ollama if enabled
        providers_config = config.get('llm_providers', {})
        ollama_config = providers_config.get('ollama', {})
        
        if ollama_config.get('enabled', False):
            try:
                from src.llm_providers.ollama import OllamaProvider
                
                ollama = OllamaProvider(
                    base_url=ollama_config.get('base_url', 'http://localhost:11434')
                )
                
                if ollama.is_available():
                    results['ollama_server'] = True
                    models = ollama.list_models()
                    logger.info(f"[OK] Ollama server running with {len(models)} models")

                    if models:
                        logger.info(f"  Available models: {', '.join(models)}")
                    else:
                        logger.warning("  [WARN] No models downloaded. Run: ollama pull llama3.2:3b")
                else:
                    logger.error("[FAIL] Ollama server not responding")
                    logger.info("  Start it with: ollama serve")
                    
            except Exception as e:
                logger.error(f"[FAIL] Error checking Ollama: {e}")
        else:
            logger.info("[SKIP] Ollama disabled in config")
        
        # Check API keys for enabled providers
        credentials = check_provider_credentials(config)
        for provider, has_key in credentials.items():
            if provider == 'ollama':
                continue
            
            if has_key:
                logger.info(f"[OK] {provider.title()} API key found")
            else:
                logger.warning(f"[WARN] {provider.title()} enabled but no API key")
        
    except Exception as e:
        logger.error(f"[FAIL] Config error: {e}")

    return results


def print_diagnostic_report(results: dict) -> None:
    """
    Print formatted diagnostic report.
    
    Args:
        results: Validation results dictionary
    """
    print("\n" + "="*60)
    print("  PIXELPROMPT ENVIRONMENT DIAGNOSTICS")
    print("="*60 + "\n")
    
    # Core requirements
    print("Core Requirements:")
    print(f"  {'[OK]' if results['python_version'] else '[FAIL]'} Python 3.10+")
    print(f"  {'[OK]' if results['pygame_ce'] else '[FAIL]'} pygame-ce")
    print(f"  {'[OK]' if results['pygame_gui'] else '[FAIL]'} pygame-gui")
    print(f"  {'[OK]' if results['requests'] else '[FAIL]'} requests")
    print(f"  {'[OK]' if results['dotenv'] else '[FAIL]'} python-dotenv")

    # Configuration
    print("\nConfiguration:")
    print(f"  {'[OK]' if results['config_valid'] else '[FAIL]'} config.json valid")

    # Services
    print("\nServices:")
    print(f"  {'[OK]' if results['ollama_server'] else '[FAIL]'} Ollama server")
    
    # Overall status
    print("\n" + "="*60)
    
    all_critical = (
        results['python_version'] and
        results['pygame_ce'] and
        results['pygame_gui'] and
        results['requests'] and
        results['dotenv'] and
        results['config_valid']
    )
    
    if all_critical:
        if results['ollama_server']:
            print("[SUCCESS] All systems ready!")
        else:
            print("[WARN] Core systems ready, but Ollama not available")
            print("   Start Ollama with: ollama serve")
    else:
        print("[ERROR] Missing required dependencies")
        print("\n   Install with: pip install -r requirements.txt")
    
    print("="*60 + "\n")


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    global logger
    
    # Parse arguments
    args = parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.debug else "INFO"
    logger = setup_logging(log_level)
    
    logger.info("="*60)
    logger.info("PixelPrompt starting...")
    logger.info("="*60)
    
    # Run validation if requested
    if args.check:
        logger.info("Running environment validation...")
        results = validate_environment()
        print_diagnostic_report(results)
        
        # Exit with appropriate code
        all_pass = all(results.values())
        return 0 if all_pass else 1
    
    # Load configuration
    try:
        config = load_config(args.config)
        logger.info(f"Loaded configuration from {args.config}")
    except Exception as e:
        show_error_dialog(f"Failed to load configuration: {e}")
        return 1
    
    # Initialize providers (Phase 0 - just test they can be created)
    try:
        from src.config_manager import get_enabled_providers
        
        enabled_providers = get_enabled_providers(config)
        providers = {}
        
        for provider_name, provider_config in enabled_providers.items():
            try:
                provider = create_provider(provider_name, provider_config)
                providers[provider_name] = provider
                logger.info(f"Initialized provider: {provider.name}")
                
                # Test availability
                if provider.is_available():
                    logger.info(f"  [OK] {provider.name} is available")
                else:
                    logger.warning(f"  [WARN] {provider.name} not responding")
                    
            except Exception as e:
                logger.error(f"Failed to initialize {provider_name}: {e}")
        
        if not providers:
            show_warning_dialog(
                "No LLM providers available!\n\n"
                "Enable at least one provider in config.json:\n"
                "- Ollama (local): Start with 'ollama serve'\n"
                "- Gemini/Claude (cloud): Add API keys to .env"
            )
            return 1
            
    except Exception as e:
        show_error_dialog(f"Provider initialization error: {e}")
        return 1
    
    # Initialize game engine
    logger.info("="*60)
    logger.info("Initializing game engine...")
    logger.info("="*60)

    try:
        from src.engine import GameEngine
        from src.entities import Agent
        from src.llm_client import LLMClient
        from src.ui import UIManager

        # Create engine
        engine = GameEngine(config)

        # Initialize LLM providers
        engine.llm_providers = providers
        engine.llm_client = LLMClient(providers)
        engine.llm_client.start()

        # Create agents from config
        for agent_config in config.get('agents', []):
            agent = Agent(agent_config, engine.world)
            engine.agents.append(agent)
            logger.info(f"Spawned agent: {agent.name}")

        # Initialize UI
        window_size = (config['window']['width'], config['window']['height'])
        engine.ui_manager = UIManager(window_size, config.get('ui', {}))

        # Auto-select first agent
        if engine.agents:
            engine.agents[0].selected = True
            engine.selected_agent = engine.agents[0]
            logger.info(f"Auto-selected agent: {engine.agents[0].name}")

        logger.info("Starting game...")
        logger.info("Controls: WASD to pan camera, Click agent to select, Type to chat, ESC to exit")

        # Run game loop
        try:
            engine.run()
        finally:
            # Cleanup
            engine.cleanup()

        logger.info("Game exited cleanly")
        return 0

    except Exception as e:
        logger.exception("Error running game")
        show_error_dialog(f"Game error: {e}")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        if logger:
            logger.exception("Fatal error")
        print(f"\n[FATAL] Fatal error: {e}")
        sys.exit(1)
