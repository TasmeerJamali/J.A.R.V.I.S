# J.A.R.V.I.S. 3.0

An intelligent desktop AI assistant inspired by the AI from Iron Man. Built with Python, React, and Electron, J.A.R.V.I.S. combines voice interaction, screen understanding, desktop automation, and proactive intelligence into a unified system.

## Features

- **Voice Interaction** — Wake word detection ("Hey Jarvis"), speech-to-text, and text-to-speech with a British voice
- **Cloud AI Brain** — Google Gemini 1.5 Flash for multimodal reasoning (screen + voice)
- **Desktop Automation** — Click, type, and press keys with human-like Bezier curve mouse movement
- **Proactive Intelligence** — 24/7 background daemon that monitors your screen and offers help when appropriate
- **Long-term Memory** — Mem0-powered episodic memory that remembers past interactions
- **Security** — Face detection via MediaPipe for user presence verification
- **Sci-Fi HUD** — Futuristic React/Electron interface with Arc Reactor animation, status panels, and command log
- **Real-time Communication** — WebSocket-powered live updates between backend and frontend

## Architecture

```
┌─────────────────────────────────────────────┐
│                  Frontend                    │
│  React + Tailwind + Framer Motion + Electron │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐│
│  │ArcReactor│ │StatusPanel│ │ CommandLog   ││
│  └──────────┘ └──────────┘ └──────────────┘│
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐│
│  │VoiceWave │ │BrainPanel│ │ CommandInput ││
│  └──────────┘ └──────────┘ └──────────────┘│
└──────────────────┬──────────────────────────┘
                   │ Socket.IO (WebSocket)
┌──────────────────┴──────────────────────────┐
│                  Backend                     │
│  FastAPI + Uvicorn + Socket.IO               │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐│
│  │Wake Word │ │   STT    │ │     TTS      ││
│  │(openWake)│ │(Whisper) │ │  (Edge-TTS)  ││
│  └──────────┘ └──────────┘ └──────────────┘│
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐│
│  │  Gemini  │ │  Memory  │ │   Security   ││
│  │  Brain   │ │  (Mem0)  │ │ (MediaPipe)  ││
│  └──────────┘ └──────────┘ └──────────────┘│
│  ┌──────────┐ ┌────────────────────────────┐│
│  │ Desktop  │ │  Continuous Perception     ││
│  │ Control  │ │  Daemon (24/7 Monitoring)  ││
│  └──────────┘ └────────────────────────────┘│
└──────────────────────────────────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS, Framer Motion, Electron |
| Communication | Socket.IO (bidirectional real-time) |
| Backend Server | FastAPI + Uvicorn |
| Cloud AI | Google Gemini 1.5 Flash (multimodal) |
| Voice Input | Faster-Whisper (STT), openWakeWord |
| Voice Output | Edge-TTS (British male voice) |
| Desktop Control | PyAutoGUI (Bezier curves) |
| Memory | Mem0 (episodic memory) |
| Security | MediaPipe (face detection) |
| Local AI (optional) | Ollama + DeepSeek-R1, Florence-2, Qwen2VL |

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Google Gemini API key ([get one here](https://makersuite.google.com/app/apikey))
- Microphone and speakers

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/TasmeerJamali/J.A.R.V.I.S.git
   cd J.A.R.V.I.S
   ```

2. **Configure environment**
   ```bash
   cp .env.example backend/.env
   # Edit backend/.env and add your GEMINI_API_KEY
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

5. **Start everything**
   ```bash
   # From project root
   ./start.sh

   # Or manually:
   # Terminal 1: cd backend && python main.py
   # Terminal 2: cd frontend && npm run dev
   ```

6. **Open the frontend** at `http://localhost:5173`

### Electron Desktop App

```bash
cd frontend
npm run electron        # Dev mode with hot reload
npm run electron:build  # Build packaged app
```

## Usage

- **Voice**: Say "Hey Jarvis" followed by your command
- **Text**: Type commands in the bottom command input bar
- **HUD Toggle**: Click the monitor icon (top-left) to switch between HUD and Reactor views

### Example Commands

- "Open Google Chrome"
- "What's on my screen?"
- "Type hello world"
- "Click on the search bar"

## Project Structure

```
J.A.R.V.I.S/
├── backend/
│   ├── api/server.py              # WebSocket + REST API server
│   ├── brain/
│   │   ├── gemini_brain.py        # Google Gemini cloud brain
│   │   ├── llm.py                 # Local LLM (Ollama, optional)
│   │   └── memory.py              # Mem0 long-term memory
│   ├── core/
│   │   ├── continuous_perception.py  # 24/7 proactive daemon
│   │   ├── security.py            # Face detection
│   │   └── vision.py              # Florence-2 vision (optional)
│   ├── skills/
│   │   ├── desktop_control.py     # Mouse/keyboard automation
│   │   └── fara_computer_control.py  # Qwen2VL agent (optional)
│   ├── voice/
│   │   ├── stt.py                 # Speech-to-text (Whisper)
│   │   ├── tts.py                 # Text-to-speech (Edge-TTS)
│   │   └── wake_word.py           # Wake word detection
│   ├── main.py                    # Backend orchestrator
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ArcReactor.jsx     # Arc Reactor animation
│   │   │   ├── BrainActivity.jsx  # AI brain status panel
│   │   │   ├── CommandInput.jsx   # Text command input
│   │   │   ├── CommandLog.jsx     # Command history log
│   │   │   ├── StatusPanel.jsx    # System status dashboard
│   │   │   ├── TargetLock.jsx     # Click target overlay
│   │   │   └── VoiceWave.jsx      # Voice activity visualizer
│   │   ├── App.jsx                # Main app with HUD layout
│   │   ├── App.css                # HUD styling
│   │   └── index.css              # Global styles
│   ├── electron/
│   │   ├── main.cjs               # Electron main process
│   │   └── preload.cjs            # Secure IPC bridge
│   └── package.json
├── .env.example                   # Environment template
├── start.sh                       # Full-stack startup script
└── README.md
```

## License

This project is for educational and personal use.
