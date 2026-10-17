# Jarvis Pro - Autonomous AI Voice & Terminal Assistant

An advanced, intelligent personal AI companion powered by Google Gemini 2.5 Flash, Microsoft Edge Neural TTS / Windows SAPI, real-time Voice Activity Detection (VAD), system automation, and Android mobile integration.

Works seamlessly on **Windows Desktop** and **Android (via Termux)**!

---

## Key Features

- **Dynamic Human Personality**: Speaks with genuine depth, wit, emotional intelligence, and conversational variety.
- **Fast Natural Voice**:
  - Windows: Edge Neural TTS with SAPI instant fallback and zero audio freezing.
  - Android (Termux): Native Android TTS via `termux-api` or interactive colored terminal dialogue.
- **Cross-Platform Dual Mode**:
  - **Voice Mode**: Adaptive microphone thresholding and wake-word detection.
  - **Terminal / Console Mode**: Fast keyboard dialogue when running in mobile/headless environments without audio drivers.
- **Comprehensive Automation**:
  - System volume, brightness, battery metrics, clipboard.
  - Application launching, browser research, YouTube media streaming.
- **Persistent Conversational Memory**: Context retention across interactions using `jarvis_brain.json`.
- **Android Companion Bridge**: WebSocket server for companion device connectivity.

---

## 💻 Running on Windows

1. **Clone repository**:
   ```bash
   git clone https://github.com/vinod673/jarvis-ai-assistant.git
   cd jarvis-ai-assistant
   ```

2. **Create virtual environment & install**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   Copy `.env.example` to `.env` and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

4. **Run Jarvis**:
   ```bash
   python jarvis.py
   ```

---

## 📱 Running on Android (Termux)

1. **Install Termux** and open it.
2. **Install prerequisites in Termux**:
   ```bash
   pkg update && pkg upgrade -y
   pkg install python git -y
   pkg install termux-api mpv -y   # Optional: For Android text-to-speech & audio
   ```
3. **Clone & Install**:
   ```bash
   git clone https://github.com/vinod673/jarvis-ai-assistant.git
   cd jarvis-ai-assistant
   pip install -r requirements.txt
   ```
4. **Configure your API Key**:
   ```bash
   cp .env.example .env
   # Edit .env and paste your GEMINI_API_KEY:
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```
5. **Run Jarvis**:
   ```bash
   python jarvis.py
   ```
   *Jarvis will initialize in Interactive Terminal Mode. You can chat, give commands, or manage your system directly from your phone!*
