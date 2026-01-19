# **Product Requirements Document: PixelPrompt v2.0**

**Status:** Draft v2.0  
**Last Updated:** 2026-01-19  
**Target:** AI-assisted development via Claude Code  
**Vision:** Multi-LLM agent swarm with cozy pixel-art visualization

---

## **0. AI Agent Context & Instructions**

> **Claude Operating Instructions:**
> 
> You are an expert Python developer specializing in pygame-ce (Community Edition) and local LLM integration via ollama. You prefer clean, modular object-oriented code with:
> - Full type hints (from `typing` module)
> - Google-style docstrings
> - Defensive error handling with try/except blocks
> - Thread-safe patterns for concurrent operations
> 
> **UI Aesthetic Rules:**
> - Background: `#2E2E3A` (slate)
> - UI Panels: `#3D3D4D` (charcoal)
> - Accents: `#7DCFB6` (mint), `#F79D84` (coral), `#FBD87F` (butter)
> - Text: `#E8E8E8` (off-white)
> - Errors: `#E57373` (soft red)
> 
> **Critical Rules:**
> - NEVER call pygame rendering functions from non-main threads
> - ALWAYS validate ollama is running before attempting connections
> - ALWAYS provide fallback behavior for missing assets
> - Use provider abstraction for all LLM calls (never hardcode Ollama)

---

## **1. Executive Summary**

**PixelPrompt** transforms local AI model interaction into a cozy, visual experience. Users chat with AI agents represented as autonomous 2D pixel characters that "think," "talk," and move around a virtual room.

**Key Differentiator:** Unlike text-only LLM interfaces, PixelPrompt makes AI feel *alive* through gamified visualization.

**MVP Scope:** Single-agent proof-of-concept with Ollama. Multi-agent swarms with mixed providers (Ollama + Gemini + Claude) are Phase 6+.

**Ultimate Vision:** A "Tamagotchi meets LM Studio" experience where each agent can run a different AI brain (local Llama, cloud Gemini, cloud Claude) all in the same virtual room.

---

## **2. Technical Stack**

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Language | Python | 3.10+ | Core runtime |
| Game Engine | pygame-ce | 2.4.0+ | Rendering & input |
| UI Library | pygame_gui | 0.6.9+ | Buttons, text inputs, panels |
| LLM Backend (MVP) | Ollama | Latest | Local model inference |
| LLM Backend (Phase 6) | Google Gemini | Latest | Cloud API (creative tasks) |
| LLM Backend (Phase 6) | Anthropic Claude | Latest | Cloud API (reasoning tasks) |
| HTTP Client | requests | 2.31.0+ | Ollama API calls |
| Config | JSON | stdlib | Settings persistence |
| Threading | threading + queue | stdlib | Non-blocking LLM calls |
| Environment | python-dotenv | 1.0.0+ | API key management |

**Installation Command (MVP):**
```bash
pip install pygame-ce>=2.4.0 pygame-gui>=0.6.9 requests>=2.31.0 python-dotenv>=1.0.0
```

**Installation Command (Phase 6):**
```bash
pip install google-generativeai>=0.8.0 anthropic>=0.39.0 tiktoken>=0.7.0
```

---

## **3. Project Structure**

```
pixelprompt/
├── main.py                      # Entry point with arg parsing
├── requirements.txt             # Pinned dependencies
├── .env.example                 # Template for API keys
├── .env                         # Actual API keys (git-ignored)
├── config.json                  # Runtime configuration (auto-generated)
├── README.md                    # Setup and usage instructions
│
├── assets/
│   ├── fonts/
│   │   └── mono.ttf            # Monospace font for UI
│   └── sprites/
│       └── agent_placeholder.png  # 20x40px fallback sprite
│
├── src/
│   ├── __init__.py
│   ├── engine.py               # Game loop & state management
│   ├── entities.py             # Agent class (sprite, state machine)
│   ├── world.py                # Camera, tilemap, collision
│   ├── config_manager.py       # JSON load/save with validation
│   ├── ui.py                   # UI overlay (pygame_gui components)
│   ├── utils.py                # Helpers (error dialogs, logging)
│   │
│   └── llm_providers/          # LLM abstraction layer
│       ├── __init__.py         # BaseLLMProvider interface
│       ├── ollama.py           # OllamaProvider (Phase 3)
│       ├── gemini.py           # GeminiProvider (Phase 6)
│       └── claude.py           # ClaudeProvider (Phase 6)
│
├── tests/
│   ├── test_entities.py
│   ├── test_llm_providers.py
│   └── test_config.py
│
└── docs/
    ├── PRD.md                  # This document
    └── ARCHITECTURE.md         # Technical design doc (Phase 4+)
```

---

## **4. Configuration Schema**

**`config.json` Example:**
```json
{
  "version": "2.0",
  "window": {
    "width": 1280,
    "height": 720,
    "resizable": true,
    "fps_target": 60
  },
  "llm_providers": {
    "ollama": {
      "enabled": true,
      "base_url": "http://localhost:11434",
      "default_model": "llama3.2:3b",
      "timeout_seconds": 30,
      "health_check_endpoint": "/api/tags"
    },
    "gemini": {
      "enabled": false,
      "api_key_env": "GEMINI_API_KEY",
      "default_model": "gemini-2.0-flash-exp",
      "rate_limit_rpm": 60
    },
    "claude": {
      "enabled": false,
      "api_key_env": "ANTHROPIC_API_KEY",
      "default_model": "claude-sonnet-4-5-20250929",
      "rate_limit_rpm": 50
    }
  },
  "agents": [
    {
      "id": "agent_001",
      "name": "Pixel",
      "provider": "ollama",
      "model": "llama3.2:3b",
      "spawn_position": [640, 360],
      "color_hex": "#7DCFB6",
      "system_prompt": "You are Pixel, a helpful assistant who lives in a virtual room. Keep responses concise and friendly.",
      "max_history": 10
    }
  ],
  "camera": {
    "pan_speed": 5,
    "bounds": {
      "min_x": 0,
      "min_y": 0,
      "max_x": 2000,
      "max_y": 2000
    }
  },
  "ui": {
    "input_box_height": 50,
    "bubble_max_width": 300,
    "bubble_padding": 10,
    "typewriter_delay_ms": 30
  }
}
```

**`.env` Example:**
```bash
# API Keys (NEVER commit this file!)
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

**Validation Requirements:**
- Must fail gracefully if malformed
- Auto-generate with defaults if missing
- Validate ollama URL format and reachability
- Check for API keys in environment when provider enabled
- Warn if enabled provider lacks credentials

---

## **5. LLM Provider Architecture**

### **5.1 Abstract Base Class**

```python
# src/llm_providers/__init__.py
from abc import ABC, abstractmethod
from typing import List, Dict, Generator, Optional

class BaseLLMProvider(ABC):
    """Abstract base for all LLM backends."""
    
    @abstractmethod
    def send_message(self, 
                    messages: List[Dict[str, str]], 
                    model: str,
                    **kwargs) -> Generator[str, None, None]:
        """
        Stream response tokens.
        
        Args:
            messages: List of {"role": "user/assistant/system", "content": "..."}
            model: Model identifier (e.g., "llama3.2:3b")
            **kwargs: Provider-specific options
            
        Yields:
            str: Text chunks as they arrive
            
        Raises:
            ConnectionError: Provider unreachable
            ValueError: Invalid model or parameters
            TimeoutError: Request exceeded timeout
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Health check for this provider.
        
        Returns:
            bool: True if provider is reachable and configured
        """
        pass
    
    @abstractmethod
    def list_models(self) -> List[str]:
        """
        Return available model names.
        
        Returns:
            List[str]: Model identifiers that can be used with send_message
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider display name (e.g., "Ollama", "Google Gemini")."""
        pass
```

### **5.2 Implementation Examples**

**Ollama Provider (Phase 3 - MVP)**
```python
# src/llm_providers/ollama.py
import requests
from typing import Generator, List, Dict
from .base import BaseLLMProvider

class OllamaProvider(BaseLLMProvider):
    """Local Ollama provider for free, offline inference."""
    
    def __init__(self, base_url: str = "http://localhost:11434", 
                 timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        
    @property
    def name(self) -> str:
        return "Ollama"
        
    def send_message(self, messages: List[Dict], model: str, 
                    **kwargs) -> Generator[str, None, None]:
        """Stream responses from Ollama's /api/chat endpoint."""
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "stream": True
        }
        
        try:
            response = requests.post(url, json=payload, 
                                    stream=True, timeout=self.timeout)
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if 'message' in chunk and 'content' in chunk['message']:
                        yield chunk['message']['content']
                        
        except requests.ConnectionError:
            raise ConnectionError(f"Cannot reach Ollama at {self.base_url}")
        except requests.Timeout:
            raise TimeoutError(f"Request timed out after {self.timeout}s")
            
    def is_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", 
                                   timeout=5)
            return response.status_code == 200
        except:
            return False
            
    def list_models(self) -> List[str]:
        """Get list of pulled models."""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        except:
            return []
```

**Gemini Provider (Phase 6)**
```python
# src/llm_providers/gemini.py
import google.generativeai as genai
from typing import Generator, List, Dict
from .base import BaseLLMProvider

class GeminiProvider(BaseLLMProvider):
    """Google Gemini cloud API provider."""
    
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.api_key = api_key
        
    @property
    def name(self) -> str:
        return "Google Gemini"
        
    def send_message(self, messages: List[Dict], model: str, 
                    **kwargs) -> Generator[str, None, None]:
        """Stream responses from Gemini API."""
        # Convert messages to Gemini format
        # System prompt goes in generation config
        # Alternate user/assistant messages
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(
            messages[-1]['content'],
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
                
    def is_available(self) -> bool:
        """Check API key validity."""
        return bool(self.api_key and len(self.api_key) > 0)
        
    def list_models(self) -> List[str]:
        """Return supported Gemini models."""
        return [
            "gemini-2.0-flash-exp",
            "gemini-2.0-flash-thinking-exp",
            "gemini-1.5-pro"
        ]
```

**Claude Provider (Phase 6)**
```python
# src/llm_providers/claude.py
import anthropic
from typing import Generator, List, Dict
from .base import BaseLLMProvider

class ClaudeProvider(BaseLLMProvider):
    """Anthropic Claude cloud API provider."""
    
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        
    @property
    def name(self) -> str:
        return "Anthropic Claude"
        
    def send_message(self, messages: List[Dict], model: str, 
                    **kwargs) -> Generator[str, None, None]:
        """Stream responses from Claude API."""
        # Extract system prompt if present
        system_prompt = next(
            (m['content'] for m in messages if m['role'] == 'system'),
            None
        )
        
        # Filter to user/assistant only
        filtered_messages = [
            m for m in messages if m['role'] in ['user', 'assistant']
        ]
        
        with self.client.messages.stream(
            model=model,
            max_tokens=1024,
            messages=filtered_messages,
            system=system_prompt
        ) as stream:
            for text in stream.text_stream:
                yield text
                
    def is_available(self) -> bool:
        """Check API key validity."""
        try:
            self.client.messages.count_tokens(
                model="claude-sonnet-4-5-20250929",
                messages=[{"role": "user", "content": "test"}]
            )
            return True
        except:
            return False
            
    def list_models(self) -> List[str]:
        """Return supported Claude models."""
        return [
            "claude-sonnet-4-5-20250929",
            "claude-opus-4-5-20251101",
            "claude-haiku-4-5-20251001"
        ]
```

---

## **6. Implementation Phases**

### **Phase 0: Foundation & Validation** *(Days 1-2)*

**Goal:** Ensure environment is ready before coding begins.

**Tasks:**

1. **Dependency Check Script** (`main.py --check`)
   ```python
   def validate_environment() -> Dict[str, bool]:
       """
       Check Python version, dependencies, and service availability.
       
       Returns:
           Dict with status for: python_version, pygame, ollama_server, api_keys
       """
       checks = {}
       
       # Check Python >= 3.10
       checks['python'] = sys.version_info >= (3, 10)
       
       # Verify pygame-ce import
       try:
           import pygame_ce
           checks['pygame'] = True
       except ImportError:
           checks['pygame'] = False
       
       # Test ollama connection
       checks['ollama'] = test_ollama_connection()
       
       # Check for API keys (if providers enabled)
       checks['api_keys'] = check_env_vars()
       
       return checks
   ```

2. **Config Manager** (`src/config_manager.py`)
   - Load/save JSON with schema validation using `jsonschema`
   - Generate default config if missing
   - Provide type-safe getters (e.g., `get_window_size() -> Tuple[int, int]`)
   - Validate provider configurations
   - Merge user config with defaults

3. **Logging Setup** (`src/utils.py`)
   - Console logger with timestamps and color coding
   - Error log file (`logs/pixelprompt.log`)
   - Different levels for debug/production
   - Log rotation (max 5MB per file)

4. **Provider Factory** (`src/llm_providers/__init__.py`)
   ```python
   def create_provider(provider_name: str, config: Dict) -> BaseLLMProvider:
       """Factory function to instantiate providers."""
       if provider_name == "ollama":
           return OllamaProvider(base_url=config['base_url'])
       elif provider_name == "gemini":
           api_key = os.getenv(config['api_key_env'])
           return GeminiProvider(api_key=api_key)
       elif provider_name == "claude":
           api_key = os.getenv(config['api_key_env'])
           return ClaudeProvider(api_key=api_key)
       else:
           raise ValueError(f"Unknown provider: {provider_name}")
   ```

**Acceptance Criteria:**
- [ ] `python main.py --check` reports "✓ All systems ready"
- [ ] Missing `config.json` auto-generates with defaults
- [ ] Invalid JSON shows user-friendly error dialog
- [ ] Ollama offline shows: "⚠️ Ollama not detected. Start it with `ollama serve`"
- [ ] Provider factory correctly instantiates all three provider types

---

### **Phase 1: The Engine & "The Room"** *(Days 3-5)*

**Goal:** Render a navigable world with a camera system.

**R1.1 Window Management** (`src/engine.py`)
```python
from enum import Enum

class GameState(Enum):
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
        
        flags = pygame.RESIZABLE if window_cfg['resizable'] else 0
        self.screen = pygame.display.set_mode(
            (window_cfg['width'], window_cfg['height']),
            flags
        )
        pygame.display.set_caption("PixelPrompt")
        
        self.clock = pygame.time.Clock()
        self.fps_target = window_cfg['fps_target']
        self.running = True
        self.state = GameState.RUNNING
        
        # Initialize subsystems
        self.world = World(config)
        self.camera_offset = pygame.math.Vector2(0, 0)
        
    def run(self) -> None:
        """Main game loop at target FPS."""
        while self.running:
            dt = self.clock.tick(self.fps_target) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.render()
            
    def handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    
    def update(self, dt: float) -> None:
        """Update game state."""
        self.update_camera(dt)
        
    def update_camera(self, dt: float) -> None:
        """Handle WASD camera movement."""
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
                bounds['max_y'],
                self.camera_offset.y + speed
            )
        if keys[pygame.K_a]:
            self.camera_offset.x = max(
                bounds['min_x'],
                self.camera_offset.x - speed
            )
        if keys[pygame.K_d]:
            self.camera_offset.x = min(
                bounds['max_x'],
                self.camera_offset.x + speed
            )
            
    def render(self) -> None:
        """Render frame."""
        self.screen.fill(pygame.Color(self.config['colors']['background']))
        self.world.render(self.screen, self.camera_offset)
        pygame.display.flip()
```

**R1.2 World Rendering** (`src/world.py`)
```python
class World:
    """Manages the game world, tilemap, and environment."""
    
    def __init__(self, config: Dict):
        """
        Initialize world from config.
        
        Args:
            config: Configuration dictionary
        """
        self.tile_size = 32
        self.floor_color = pygame.Color("#3D3D4D")
        self.grid_color = pygame.Color("#2E2E3A")
        
        # Calculate world size from camera bounds
        bounds = config['camera']['bounds']
        self.width = bounds['max_x']
        self.height = bounds['max_y']
        
    def render(self, surface: pygame.Surface, 
               camera_offset: pygame.math.Vector2) -> None:
        """
        Draw tiled floor with camera offset applied.
        
        Args:
            surface: Pygame surface to draw on
            camera_offset: Camera position for viewport scrolling
        """
        screen_width, screen_height = surface.get_size()
        
        # Calculate visible tile range
        start_x = int(camera_offset.x // self.tile_size)
        start_y = int(camera_offset.y // self.tile_size)
        end_x = start_x + (screen_width // self.tile_size) + 2
        end_y = start_y + (screen_height // self.tile_size) + 2
        
        # Draw tiles
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * self.tile_size - camera_offset.x
                screen_y = y * self.tile_size - camera_offset.y
                
                # Draw tile
                pygame.draw.rect(
                    surface,
                    self.floor_color,
                    (screen_x, screen_y, self.tile_size, self.tile_size)
                )
                
                # Draw grid lines
                pygame.draw.rect(
                    surface,
                    self.grid_color,
                    (screen_x, screen_y, self.tile_size, self.tile_size),
                    1  # 1px border
                )
```

**R1.3 Camera System**
- WASD keys pan viewport
- Constrained to `camera.bounds` from config
- Smooth movement at consistent speed
- No zoom functionality (MVP - add in Phase 5+)

**Acceptance Criteria:**
- [ ] Window opens at configured resolution (1280x720)
- [ ] Tiled floor visible with 32x32 grid
- [ ] WASD pans camera smoothly within bounds
- [ ] Camera cannot pan beyond defined bounds
- [ ] ESC key cleanly exits application
- [ ] Window resize updates viewport correctly
- [ ] FPS counter stable at target (60 FPS)

---

### **Phase 2: The Agent (Sprite & State Machine)** *(Days 6-8)*

**Goal:** Create an autonomous character with animated states.

**R2.1 Agent Entity** (`src/entities.py`)
```python
from enum import Enum
from typing import Optional, Tuple
import random

class AgentState(Enum):
    """Agent behavior states."""
    IDLE = "idle"          # Random walks every 3-5s
    THINKING = "thinking"  # Paces quickly
    TALKING = "talking"    # Stands still, bobs
    ERROR = "error"        # Red outline, shows error bubble

class Agent(pygame.sprite.Sprite):
    """AI agent sprite with state machine and animations."""
    
    def __init__(self, config: Dict, world: World):
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
        self.position = pygame.math.Vector2(config['spawn_position'])
        self.target_position = self.position.copy()
        self.move_speed = 50.0  # pixels/second
        
        # Visuals
        self.color = pygame.Color(config['color_hex'])
        self.size = (20, 40)  # width, height
        self.selected = False
        
        # Animation
        self.bob_offset = 0.0
        self.bob_direction = 1
        
        # Communication
        self.speech_bubble: Optional[SpeechBubble] = None
        self.conversation_history: List[Dict] = []
        self.max_history = config['max_history']
        
        # Create sprite surface
        self._create_sprite()
        
    def _create_sprite(self) -> None:
        """Create placeholder sprite or load from file."""
        sprite_path = f"assets/sprites/{self.id}.png"
        
        if os.path.exists(sprite_path):
            self.image = pygame.image.load(sprite_path)
        else:
            # Procedural rectangle sprite
            self.image = pygame.Surface(self.size)
            self.image.fill(self.color)
            
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        
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
        self.position.y += math.sin(self.bob_offset) * bob_amplitude * dt
        
    def _update_error(self, dt: float) -> None:
        """Error state: shake horizontally."""
        if self.state_timer < 2.0:
            shake_amount = 3 * math.sin(self.state_timer * 20)
            self.position.x += shake_amount
        else:
            # Return to idle
            self.set_state(AgentState.IDLE)
            
    def _pick_random_target(self) -> None:
        """Pick a random position within 2 tiles."""
        offset_x = random.randint(-64, 64)
        offset_y = random.randint(-64, 64)
        self.target_position = self.position + pygame.math.Vector2(offset_x, offset_y)
        
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
            
        # Draw speech bubble
        if self.speech_bubble:
            bubble_pos = (screen_pos[0], screen_pos[1] - 50)
            self.speech_bubble.render(surface, bubble_pos)
```

**R2.2 Animation Details**

| State | Behavior | Duration | Speed Multiplier |
|-------|----------|----------|------------------|
| IDLE | Walk to random nearby tile (±2 tiles) | 3-5s random | 1x |
| THINKING | Pace 2 tiles left/right | Until LLM response | 3x |
| TALKING | Bob up/down 2px at 0.5Hz | While bubble visible | 0x (stationary) |
| ERROR | Shake horizontally ±3px at 20Hz | 2 seconds | 0x (stationary) |

**R2.3 Visuals**
- If `assets/sprites/{agent.id}.png` exists: load and use it (20x40px recommended)
- Else: Render filled rectangle with `agent.color_hex`
- Selected state: Draw 2px white outline (`#E8E8E8`)
- Error state: Draw 2px red outline (`#E57373`) with shake animation

**Acceptance Criteria:**
- [ ] Agent spawns at configured position
- [ ] Clicking agent toggles selection highlight
- [ ] Idle state: agent walks autonomously every 3-5s
- [ ] Placeholder rectangle renders if sprite PNG missing
- [ ] Agent stays within world bounds
- [ ] State transitions work correctly (idle → thinking → talking → idle)
- [ ] Multiple state changes don't cause visual glitches

---

### **Phase 3: The Brain (Ollama Integration)** *(Days 9-12)*

**Goal:** Connect agent to LLM with thread-safe, non-blocking calls using provider abstraction.

**R3.1 Threaded LLM Client** (`src/llm_client.py`)
```python
import threading
from queue import Queue, Empty
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class LLMClient:
    """
    Thread-safe LLM client supporting multiple providers.
    
    Manages request/response queues and background worker thread
    to prevent blocking the main game loop.
    """
    
    def __init__(self, providers: Dict[str, BaseLLMProvider]):
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
        
    def start(self) -> None:
        """Launch background worker thread."""
        if self.worker_thread is not None:
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
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            self.worker_thread = None
            
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
            'history': history
        })
        logger.debug(f"Queued message for {agent_id} via {provider_name}")
        
    def get_response(self) -> Optional[Dict]:
        """
        Check for completed responses (non-blocking).
        
        Returns:
            Dict with 'agent_id', 'status' ('success'/'error'), 
            'text' or 'error' field
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
                response_text = self._call_llm(request)
                self.response_queue.put({
                    'agent_id': request['agent_id'],
                    'status': 'success',
                    'text': response_text
                })
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
        
        # Build message list
        messages = request['history'].copy()
        messages.append({
            'role': 'user',
            'content': request['message']
        })
        
        # Stream response and accumulate
        response_chunks = []
        for chunk in provider.send_message(messages, request['model']):
            response_chunks.append(chunk)
            
            # Optional: Push partial responses to queue for typewriter effect
            # self.response_queue.put({
            #     'agent_id': request['agent_id'],
            #     'status': 'partial',
            #     'text': ''.join(response_chunks)
            # })
            
        return ''.join(response_chunks)
```

**R3.2 Integration with Game Loop** (`src/engine.py`)
```python
class GameEngine:
    def __init__(self, config: Dict):
        # ... existing init code ...
        
        # Initialize LLM providers
        self.llm_providers = self._initialize_providers(config)
        self.llm_client = LLMClient(self.llm_providers)
        self.llm_client.start()
        
    def _initialize_providers(self, config: Dict) -> Dict[str, BaseLLMProvider]:
        """Create provider instances from config."""
        from src.llm_providers import create_provider
        
        providers = {}
        provider_configs = config['llm_providers']
        
        for name, cfg in provider_configs.items():
            if cfg.get('enabled', False):
                try:
                    providers[name] = create_provider(name, cfg)
                    logger.info(f"Initialized provider: {name}")
                except Exception as e:
                    logger.error(f"Failed to init {name}: {e}")
                    
        return providers
        
    def update(self, dt: float) -> None:
        # ... existing update code ...
        
        # Process LLM responses
        self._process_llm_responses()
        
    def _process_llm_responses(self) -> None:
        """Check for and handle LLM responses from queue."""
        while True:
            response = self.llm_client.get_response()
            if response is None:
                break
                
            agent = self._get_agent_by_id(response['agent_id'])
            if agent is None:
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
                
            elif response['status'] == 'error':
                # Show error in bubble
                error_msg = self._format_error(response['error'])
                agent.speech_bubble = SpeechBubble(
                    text=error_msg,
                    max_width=self.config['ui']['bubble_max_width'],
                    is_error=True
                )
                agent.set_state(AgentState.ERROR)
                
    def _format_error(self, error: str) -> str:
        """Convert technical errors to user-friendly messages."""
        if 'ConnectionError' in error or 'Cannot reach' in error:
            return "🔌 Can't reach LLM service"
        elif 'TimeoutError' in error or 'timed out' in error:
            return "⏱️ Request timed out"
        elif '404' in error or 'not found' in error:
            return "📦 Model not found"
        else:
            return f"⚠️ Error: {error[:50]}"
            
    def cleanup(self) -> None:
        """Clean shutdown."""
        self.llm_client.stop()
        pygame.quit()
```

**R3.3 Error Handling Matrix**

| Error Type | Detection | User Message | Recovery |
|------------|-----------|--------------|----------|
| Ollama offline | `ConnectionError` | "🔌 Can't reach Ollama. Start with `ollama serve`" | Retry button |
| Model not downloaded | HTTP 404 | "📦 Model not found. Run `ollama pull {model}`" | Show install command |
| Timeout | 30s no response | "⏱️ Request timed out. Try a smaller model?" | Cancel request |
| Invalid API key | 401/403 | "🔑 Invalid API key for {provider}" | Settings button |
| Rate limit | 429 | "🚦 Rate limit reached. Wait {wait_time}s" | Auto-retry |
| Invalid response | JSON parse error | "⚠️ Unexpected response format" | Report bug |

**Acceptance Criteria:**
- [ ] Sending message doesn't freeze game (60 FPS maintained)
- [ ] Agent enters THINKING state when request sent
- [ ] Response appears in speech bubble after 2-10 seconds
- [ ] Connection errors show helpful messages
- [ ] Timeout after 30s with error bubble
- [ ] Multiple rapid requests queue properly
- [ ] Worker thread stops cleanly on exit
- [ ] Provider selection works (test with mock providers)

---

### **Phase 4: The Interface (UI Layer)** *(Days 13-15)*

**Goal:** Chat input and visual feedback for agent responses.

**R4.1 UI Manager** (`src/ui.py`)
```python
import pygame
import pygame_gui
from typing import Optional, Tuple

class UIManager:
    """Manages all pygame_gui elements."""
    
    def __init__(self, screen_size: Tuple[int, int], config: Dict):
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
        
    def _setup_chat_bar(self, screen_size: Tuple[int, int]) -> None:
        """Create bottom-anchored input bar."""
        width, height = screen_size
        bar_height = self.config['input_box_height']
        
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
        # Recreate chat bar with new dimensions
        self._setup_chat_bar(new_size)
```

**R4.2 Speech Bubbles** (`src/ui.py`)
```python
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
            self.bg_color = pygame.Color("#E57373")
            self.text_color = pygame.Color("#FFFFFF")
        else:
            self.bg_color = pygame.Color("#FFFFFF")
            self.text_color = pygame.Color("#2E2E3A")
            
        # Font
        self.font = pygame.font.Font(None, 24)
        
        # Auto-dismiss timer
        self.lifetime = 10.0  # seconds
        self.age = 0.0
        
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
        # Word wrap text
        wrapped_lines = self._wrap_text(self.displayed_text)
        
        # Calculate bubble size
        line_height = self.font.get_linesize()
        text_height = len(wrapped_lines) * line_height
        text_width = max(
            self.font.size(line)[0] for line in wrapped_lines
        )
        
        bubble_width = text_width + self.padding * 2
        bubble_height = text_height + self.padding * 2
        
        # Position bubble above agent (centered)
        bubble_x = position[0] - bubble_width // 2
        bubble_y = position[1] - bubble_height - 10  # 10px gap
        
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
        
        # Draw pointer triangle
        tip_x = position[0]
        tip_y = position[1] - 10
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
```

**R4.3 Integration with Game Loop**
```python
class GameEngine:
    def __init__(self, config: Dict):
        # ... existing code ...
        self.ui_manager = UIManager(
            (config['window']['width'], config['window']['height']),
            config['ui']
        )
        self.selected_agent: Optional[Agent] = None
        
    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_agent_click(event.pos)
                    
            elif event.type == pygame.VIDEORESIZE:
                self.ui_manager.resize(event.size)
                
            # Process UI events
            message = self.ui_manager.process_events(event)
            if message:
                self._send_message_to_agent(message)
                
    def _handle_agent_click(self, mouse_pos: Tuple[int, int]) -> None:
        """Check if any agent was clicked."""
        for agent in self.agents:
            if agent.handle_click(mouse_pos, self.camera_offset):
                # Deselect others
                for a in self.agents:
                    a.selected = False
                # Select this one
                agent.selected = True
                self.selected_agent = agent
                break
                
    def _send_message_to_agent(self, message: str) -> None:
        """Send message to selected agent."""
        if self.selected_agent is None:
            # Auto-select first agent if none selected
            if self.agents:
                self.selected_agent = self.agents[0]
                self.selected_agent.selected = True
            else:
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
            
        # Set thinking state
        agent.set_state(AgentState.THINKING)
        
        # Queue LLM request
        self.llm_client.send_message(
            agent_id=agent.id,
            provider_name=agent.provider_name,
            model=agent.model,
            message=message,
            history=agent.conversation_history
        )
```

**Acceptance Criteria:**
- [ ] Text input focused by default on startup
- [ ] Enter key sends message (same as button click)
- [ ] Empty/whitespace messages not sent
- [ ] Speech bubble appears above selected agent
- [ ] Typewriter effect smooth at 60 FPS
- [ ] Bubble disappears after 10 seconds
- [ ] Word wrapping works correctly (no overflow)
- [ ] Bubble truncates to 5 lines with "..."
- [ ] Error bubbles use red styling
- [ ] Clicking agent selects it for messages
- [ ] Auto-selects first agent if none selected
- [ ] Window resize updates UI layout

---

### **Phase 5: Polish & Multi-Agent Foundation** *(Days 16-17)*

**Goal:** Add quality-of-life features and prepare for multi-agent support.

**R5.1 Agent Selection Improvements**
- Visual indicator for selected agent (glowing outline animation)
- Keyboard shortcuts: Tab cycles through agents
- Click empty space deselects all
- Selected agent name shown in UI

**R5.2 Agent Management UI**
- "Add Agent" button in UI
- Modal dialog:
  - Name input
  - Provider dropdown (shows only enabled providers)
  - Model dropdown (populated from `provider.list_models()`)
  - Color picker
  - System prompt text area
- "Remove Agent" button (with confirmation)
- Save/load agent configurations

**R5.3 Configuration UI**
- Settings button
- Settings modal with tabs:
  - **Providers**: Enable/disable, test connection, API key input
  - **Performance**: FPS target, typewriter speed
  - **Appearance**: Colors, bubble size
  - **Advanced**: Logging level, cache settings

**R5.4 Quality of Life**
- FPS counter toggle (F3 key)
- Screenshot key (F12)
- Conversation export (JSON format)
- Error notification toasts
- Loading spinner during first LLM call

**Acceptance Criteria:**
- [ ] Can add new agent without editing config
- [ ] Provider health check shows status
- [ ] Settings persist across restarts
- [ ] Keyboard shortcuts documented in README
- [ ] All UI elements scale with window resize

---

### **Phase 6: Cloud Provider Integration** *(Days 18-20)*

**Goal:** Enable Gemini and Claude providers with proper API key management.

**R6.1 Provider Implementation**
- Complete `GeminiProvider` class (see architecture section)
- Complete `ClaudeProvider` class (see architecture section)
- Test with all three providers simultaneously

**R6.2 API Key Management**
- First-run wizard for API key setup
- Masked input fields
- "Test Connection" buttons with status indicators
- Links to provider signup pages:
  - Gemini: https://aistudio.google.com/apikey
  - Claude: https://console.anthropic.com/

**R6.3 Cost Tracking (Optional)**
- Token counter using `tiktoken`
- Daily spend estimate
- Warning at 80% of user-defined budget
- Per-agent cost breakdown

**R6.4 Rate Limiting**
- Respect provider rate limits
- Queue requests if limit reached
- Show wait time to user
- Auto-retry after backoff period

**Acceptance Criteria:**
- [ ] Gemini provider works with valid API key
- [ ] Claude provider works with valid API key
- [ ] Can have agents with different providers in same session
- [ ] Invalid API keys show helpful error messages
- [ ] Rate limit warnings appear before hitting limit
- [ ] Token counting accurate (within 5%)

---

## **7. Error Handling & Resilience**

### **7.1 Startup Checks**
```python
def main():
    """Entry point with comprehensive validation."""
    
    # Parse arguments
    args = parse_args()
    
    if args.check:
        # Run diagnostics
        results = validate_environment()
        print_diagnostic_report(results)
        sys.exit(0 if all(results.values()) else 1)
        
    # Load config
    try:
        config = load_config('config.json')
    except Exception as e:
        show_error_dialog(f"Config Error: {e}")
        config = generate_default_config()
        save_config('config.json', config)
        
    # Verify at least one provider available
    if not any(p['enabled'] for p in config['llm_providers'].values()):
        show_warning(
            "No LLM providers enabled. "
            "Enable at least one in config.json or Settings."
        )
        
    # Launch game
    try:
        engine = GameEngine(config)
        engine.run()
    except Exception as e:
        logger.exception("Fatal error")
        show_error_dialog(f"Fatal Error: {e}")
        sys.exit(1)
    finally:
        engine.cleanup()
```

### **7.2 Runtime Error Recovery**

| Scenario | Detection | Recovery Strategy |
|----------|-----------|-------------------|
| Provider disconnects mid-conversation | Response queue timeout | Retry once, then show error bubble |
| Invalid model name | Provider raises ValueError | Suggest valid models from `list_models()` |
| Out of memory | MemoryError exception | Clear conversation history, suggest restart |
| Config corruption | JSON parse error | Load defaults, backup corrupted file |
| Asset missing | File not found | Use procedural fallback, log warning |
| Window loses focus | pygame.ACTIVEEVENT | Pause animations, mute sounds |

---

## **8. Testing Strategy**

### **8.1 Unit Tests** (pytest)
```bash
tests/
├── test_config_manager.py     # JSON validation, defaults
├── test_entities.py            # Agent state machine
├── test_llm_providers.py       # Mock API responses
├── test_ui.py                  # Text wrapping, bubble rendering
└── test_world.py               # Collision detection, tile rendering
```

**Example Test:**
```python
def test_agent_state_transition():
    """Verify IDLE -> THINKING -> TALKING flow."""
    agent = Agent(test_config, test_world)
    
    assert agent.state == AgentState.IDLE
    
    agent.set_state(AgentState.THINKING)
    assert agent.state == AgentState.THINKING
    
    agent.speech_bubble = SpeechBubble("Hello", 300)
    agent.set_state(AgentState.TALKING)
    assert agent.state == AgentState.TALKING
```

### **8.2 Integration Tests**
- Mock Ollama with `responses` library
- Test full request → queue → response → bubble flow
- Verify thread safety with concurrent requests

### **8.3 Manual Test Checklist**
- [ ] Fresh install on Python 3.10 (clean virtualenv)
- [ ] Works with Ollama offline (shows errors gracefully)
- [ ] Test with 3 different models (small, medium, large)
- [ ] Window resize doesn't break UI layout
- [ ] 30+ message conversation (tests history trimming)
- [ ] Multiple agents with different providers
- [ ] Rapid-fire messages don't crash (stress test)
- [ ] Alt+Tab doesn't corrupt game state
- [ ] Config changes persist across restarts

---

## **9. Performance Targets**

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **FPS** | 60 | `pygame.time.Clock.get_fps()` |
| **LLM Response Time** | < 5s (3B model on CPU) | Timestamp delta |
| **Memory Usage** | < 200MB | `psutil.Process().memory_info()` |
| **Startup Time** | < 2s to window visible | Time from `main()` to first frame |
| **UI Responsiveness** | < 16ms input latency | Event processing time |
| **Provider Overhead** | < 100ms per call | Thread queue latency |

**Optimization Notes:**
- Profile with `cProfile` if FPS drops below 45
- Use sprite sheets for multiple agents (reduce blit calls)
- Consider pygame's dirty rect system for partial redraws
- Cache font rendering for repeated text

---

## **10. Known Limitations (MVP)**

**Will NOT be implemented in initial release:**
- ✗ Conversation export/history saving to disk
- ✗ Custom sprite upload UI (requires manual file placement)
- ✗ Multi-language support (English only)
- ✗ Agent-to-agent communication
- ✗ Voice input/output (TTS/STT)
- ✗ Mobile or web version
- ✗ Multiplayer/shared rooms
- ✗ Plugin system for custom providers
- ✗ Built-in model downloader UI
- ✗ Advanced animations (skeletal, procedural)

**Future Roadmap (Post-MVP):**
- Phase 7: Conversation persistence
- Phase 8: Agent-to-agent dialogue
- Phase 9: Custom agent sprites editor
- Phase 10: Plugin system

---

## **11. Development Timeline**

```
Phase 0: Foundation          [Days 1-2]  ████
Phase 1: Engine & World      [Days 3-5]  ██████
Phase 2: Agent Entity        [Days 6-8]  ██████
Phase 3: LLM Integration     [Days 9-12] ████████
Phase 4: UI Layer            [Days 13-15] ██████
Phase 5: Polish              [Days 16-17] ████
Phase 6: Cloud Providers     [Days 18-20] ██████

Testing & Bug Fixes          [Days 21-22] ████
Documentation & Packaging    [Days 23-24] ████
```

**Total Estimated Time:** 24 development days (~5 weeks part-time, ~3 weeks full-time)

---

## **12. Success Metrics**

### **Phase Completion Checklist**

**Phase 0: Foundation** ✅
- [ ] All dependencies install without errors
- [ ] Ollama health check passes
- [ ] Config validation catches malformed JSON
- [ ] Provider factory instantiates all types

**Phase 1: Engine & World** ✅
- [ ] Window opens at 1280x720
- [ ] Tiled floor renders correctly
- [ ] WASD controls feel responsive
- [ ] Maintains 60 FPS with no visible stutter

**Phase 2: Agent Entity** ✅
- [ ] Agent spawns and moves autonomously
- [ ] Click selection works reliably
- [ ] All state transitions animate correctly
- [ ] Placeholder sprite renders if PNG missing

**Phase 3: LLM Integration** ✅
- [ ] First Ollama response under 10s
- [ ] No game freezing during inference
- [ ] Error states show helpful messages
- [ ] Thread cleanup on exit is clean

**Phase 4: UI Layer** ✅
- [ ] Chat input is intuitive
- [ ] Speech bubbles render with correct wrapping
- [ ] Typewriter effect is smooth
- [ ] Window resize updates UI correctly

**Phase 5: Polish** ✅
- [ ] Settings persist across restarts
- [ ] Agent management UI works
- [ ] FPS counter toggles correctly

**Phase 6: Cloud Providers** ✅
- [ ] Gemini provider functional
- [ ] Claude provider functional
- [ ] Mixed-provider agents work together
- [ ] API key validation prevents bad requests

---

## **13. MVP Definition of Done**

> **A user can:**
> 1. Launch the app without crashes
> 2. See a pixel art agent walking around
> 3. Click the agent to select it
> 4. Type "Tell me a joke" and press Enter
> 5. Watch the agent pace while "thinking"
> 6. Read the joke in a speech bubble with typewriter effect
> 7. Continue the conversation for 10+ messages
> 8. Add a second agent using a different LLM provider
> 9. Switch between agents by clicking them
> 10. Close the app cleanly with ESC

**Success = All 10 steps work without errors on a fresh Python 3.10 install**

---

## **14. Recommended Development Workflow**

### **14.1 Phase Execution Command Templates**

**Phase 0:**
```
"Claude Code: Implement Phase 0 from the PRD. Create config_manager.py with 
schema validation, utils.py with logging setup, and llm_providers/__init__.py 
with the BaseLLMProvider interface and factory function. Generate a default 
config.json. Add environment validation that checks Python version, dependencies, 
and Ollama availability."
```

**Phase 1:**
```
"Claude Code: Implement Phase 1 from the PRD. Create engine.py with the main 
game loop, world.py with tiled floor rendering, and implement WASD camera 
controls with bounds checking. Target 60 FPS."
```

**Phase 2:**
```
"Claude Code: Implement Phase 2 from the PRD. Create entities.py with the Agent 
class, AgentState enum, and state machine logic. Implement IDLE, THINKING, 
TALKING, and ERROR states with appropriate animations. Add click detection."
```

**Phase 3:**
```
"Claude Code: Implement Phase 3 from the PRD. Create llm_client.py with 
thread-safe request/response queues. Implement OllamaProvider in 
llm_providers/ollama.py with streaming support. Integrate with game loop 
for non-blocking LLM calls."
```

**Phase 4:**
```
"Claude Code: Implement Phase 4 from the PRD. Create ui.py with pygame_gui 
integration for chat input. Implement SpeechBubble class with typewriter 
effect and word wrapping. Add UI event handling to engine."
```

### **14.2 Git Workflow**
```bash
# Start each phase with a branch
git checkout -b phase-1-engine

# Commit after each sub-task
git commit -m "feat: add camera panning with WASD"

# Merge after passing acceptance criteria
git checkout main
git merge phase-1-engine
```

### **14.3 Testing Cadence**
- Run unit tests after each commit
- Run integration tests after each phase
- Manual test checklist before merging to main

---

## **15. Recommended Model Configurations**

### **For Development & Testing:**
```json
{
  "agents": [
    {
      "name": "Pixel",
      "provider": "ollama",
      "model": "llama3.2:3b",
      "system_prompt": "You are Pixel. Give very short, friendly responses (1-2 sentences max)."
    }
  ]
}
```
**Why:** Fast responses for rapid iteration.

### **For Demo/Production:**
```json
{
  "agents": [
    {
      "name": "Pixel",
      "provider": "ollama",
      "model": "llama3.2:3b",
      "system_prompt": "You are Pixel, a cozy virtual companion. Be warm and concise."
    },
    {
      "name": "Gemma",
      "provider": "gemini",
      "model": "gemini-2.0-flash-exp",
      "system_prompt": "You are Gemma, a creative writer. Respond with vivid imagery in 2-3 sentences."
    },
    {
      "name": "Claude Jr.",
      "provider": "claude",
      "model": "claude-sonnet-4-5-20250929",
      "system_prompt": "You are Claude Jr., a thoughtful analyst. Give clear, structured answers in 3-4 sentences."
    }
  ]
}
```
**Why:** Demonstrates multi-provider capabilities with distinct personalities.

---

## **16. Troubleshooting Guide**

### **Common Issues:**

**"Cannot reach Ollama"**
```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

**"Model not found"**
```bash
# List available models
ollama list

# Pull missing model
ollama pull llama3.2:3b
```

**"pygame-ce not found"**
```bash
# Ensure you're installing pygame-ce, not pygame
pip uninstall pygame pygame-ce
pip install pygame-ce>=2.4.0
```

**"API key invalid"**
```bash
# Check .env file exists and has correct format
cat .env

# Verify environment variable is set
python -c "import os; print(os.getenv('GEMINI_API_KEY'))"
```

**"FPS drops below 60"**
- Reduce number of agents
- Lower typewriter speed
- Disable debug logging
- Use smaller models

---

## **17. Next Steps for Developer**

### **Immediate Actions:**

1. **Environment Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   
   # Install dependencies
   pip install pygame-ce>=2.4.0 pygame-gui>=0.6.9 requests>=2.31.0 python-dotenv>=1.0.0
   
   # Start Ollama (separate terminal)
   ollama serve
   
   # Pull model
   ollama pull llama3.2:3b
   
   # Create directory structure
   mkdir -p src/llm_providers assets/sprites tests docs logs
   touch src/__init__.py src/llm_providers/__init__.py
   ```

2. **Initialize Git**
   ```bash
   git init
   echo "venv/" >> .gitignore
   echo ".env" >> .gitignore
   echo "*.pyc" >> .gitignore
   echo "__pycache__/" >> .gitignore
   echo "logs/" >> .gitignore
   git add .
   git commit -m "Initial commit: PRD and project structure"
   ```

3. **Start Phase 0**
   - Use the Phase 0 command template from section 14.1
   - Run validation checks
   - Verify config generation
   - Test provider factory

---

## **18. Questions Before Starting**

### **Configuration Decisions:**

1. **Ollama Model:** 
   - Recommended: `llama3.2:3b` (fast, good quality)
   - Alternative: `qwen2.5:3b` (faster, multilingual)
   - Alternative: `phi4:latest` (best reasoning, slower)

2. **Window Size:**
   - 1280x720 (16:9, most common)
   - 1920x1080 (Full HD, larger displays)
   - 800x600 (Retro aesthetic, lower-end hardware)

3. **Debug Features:**
   - Enable FPS counter by default? (F3 to toggle)
   - Show collision boxes in debug mode?
   - Add verbose logging for development?

4. **Cloud Providers:**
   - Get API keys now or wait until Phase 6?
   - Set usage budgets/limits?

---

## **19. Additional Resources**

- **Pygame-ce Docs:** https://pyga.me/docs/
- **Pygame GUI Docs:** https://pygame-gui.readthedocs.io/
- **Ollama API Docs:** https://github.com/ollama/ollama/blob/main/docs/api.md
- **Gemini API Docs:** https://ai.google.dev/gemini-api/docs
- **Claude API Docs:** https://docs.anthropic.com/

---

**This PRD is ready for AI-assisted implementation via Claude Code!** 🚀

Just paste the Phase 0 command and we'll start building.
