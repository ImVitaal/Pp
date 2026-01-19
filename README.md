# PixelPrompt

**Visualize your local AI models as autonomous pixel-art characters in a cozy virtual room.**

![Version](https://img.shields.io/badge/version-0.1.0--alpha-orange)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🎮 What is PixelPrompt?

PixelPrompt transforms AI interaction into a visual, gamified experience. Chat with AI agents represented as 2D pixel characters that think, talk, and move autonomously. Each agent can run a different AI brain - local models via Ollama, or cloud APIs like Gemini and Claude.

**Features:**
- 🤖 Autonomous pixel-art AI agents with state animations
- 💬 Speech bubbles with typewriter effects
- 🎨 Cozy pastel aesthetic
- 🔌 Multi-provider support (Ollama, Gemini, Claude)
- 🎯 Non-blocking threaded LLM calls
- 🎪 Expandable agent swarm

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **Ollama** (for local models)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd pixelprompt
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start Ollama** (separate terminal):
   ```bash
   ollama serve
   ```

5. **Pull a model:**
   ```bash
   ollama pull llama3.2:3b
   ```

6. **Run environment check:**
   ```bash
   python main.py --check
   ```

7. **Launch PixelPrompt:**
   ```bash
   python main.py
   ```

## 🎮 How to Use

1. **Launch the app** - A window opens with your first agent
2. **Click an agent** to select it (white outline appears)
3. **Type a message** in the input box at the bottom
4. **Press Enter** or click "Send"
5. **Watch the agent think** (pacing animation)
6. **Read the response** in a speech bubble

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| **WASD** | Pan camera |
| **ESC** | Exit |
| **Enter** | Send message |
| **F3** | Toggle FPS counter (Phase 5+) |
| **F12** | Screenshot (Phase 5+) |

## ⚙️ Configuration

Edit `config.json` to customize:

```json
{
  "window": {
    "width": 1280,
    "height": 720,
    "fps_target": 60
  },
  "agents": [
    {
      "name": "Pixel",
      "provider": "ollama",
      "model": "llama3.2:3b",
      "color_hex": "#7DCFB6"
    }
  ]
}
```

### Recommended Models

| Model | Speed | Quality | Size | Use Case |
|-------|-------|---------|------|----------|
| `llama3.2:3b` | ⚡⚡⚡ | ★★★ | 2GB | MVP, fast responses |
| `qwen2.5:3b` | ⚡⚡⚡ | ★★★ | 2GB | Multilingual |
| `phi4:latest` | ⚡⚡ | ★★★★ | 7GB | Best reasoning |

## 🔌 Cloud Providers (Phase 6)

To use Gemini or Claude:

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Add API keys to `.env`:**
   ```bash
   GEMINI_API_KEY=your_key_here
   ANTHROPIC_API_KEY=your_key_here
   ```

3. **Enable in config.json:**
   ```json
   "llm_providers": {
     "gemini": {
       "enabled": true,
       "default_model": "gemini-2.0-flash-exp"
     }
   }
   ```

## 🐛 Troubleshooting

### "Cannot reach Ollama"
```bash
# Check if running
ollama list

# Start server
ollama serve
```

### "Model not found"
```bash
ollama pull llama3.2:3b
```

### "pygame-ce not found"
```bash
pip uninstall pygame pygame-ce
pip install pygame-ce>=2.4.0
```

### FPS drops below 60
- Use smaller models (3B instead of 7B+)
- Reduce number of agents
- Lower typewriter speed in config

## 📚 Documentation

- **[PRD](docs/PRD.md)** - Complete product requirements
- **[Architecture](docs/ARCHITECTURE.md)** - Technical design (Phase 4+)

## 🛣️ Roadmap

- [x] **Phase 0**: Foundation & validation
- [ ] **Phase 1**: Game engine & world
- [ ] **Phase 2**: Agent sprites & state machine
- [ ] **Phase 3**: LLM integration (Ollama)
- [ ] **Phase 4**: UI & speech bubbles
- [ ] **Phase 5**: Polish & multi-agent
- [ ] **Phase 6**: Cloud providers (Gemini/Claude)

## 🤝 Contributing

This project is in active development. See `docs/PRD.md` for implementation details.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [pygame-ce](https://pyga.me/)
- Powered by [Ollama](https://ollama.ai/)
- UI via [pygame-gui](https://pygame-gui.readthedocs.io/)

---

**Status:** Phase 0 (Foundation) ✅ | Phase 1 (Engine) 🚧
