# Jarvis Pro - Autonomous AI Voice Assistant

An advanced, intelligent AI Voice Assistant powered by Google Gemini 2.5 Flash, Windows SAPI / Neural TTS, real-time voice activity detection (VAD), system automation, and Android mobile integration.

## Key Features

- **Fast & Natural Voice Interaction**: Hybrid Windows SAPI / Neural text-to-speech engine with zero lag.
- **Dynamic Human Personality**: Responds with warmth, wit, and conversational variety powered by Gemini 2.5 Flash.
- **Real-Time Voice Activity Detection (VAD)**: Adaptive microphone thresholding and wake-word detection.
- **System Automation & Control**:
  - Volume, brightness, battery, system status monitoring.
  - Application launching, window minimization/maximization.
  - Browser research, web searches, and YouTube media playback.
- **Persistent Memory**: Conversational memory manager (`jarvis_brain.json`) for multi-turn context retention.
- **Android Bridge**: Real-time WebSocket connection to Android companion device.

## Setup & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/vinod673/jarvis-ai-assistant.git
   cd jarvis-ai-assistant
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**:
   Copy `.env.example` to `.env` and insert your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

5. **Run Jarvis**:
   ```bash
   python jarvis.py
   ```
