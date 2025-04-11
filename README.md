# 🎙️ Voice-to-Text Obsidian Helper

Turn your voice into Obsidian notes! This Python-based tool makes it super easy to record your thoughts and automatically transcribe them into your Obsidian vault.

## ✨ Features

- 🎤 Smart voice recording that automatically stops after silence
- 🤖 AI-powered transcription using OpenAI's Whisper model
- 📝 Automatic note creation in your Obsidian vault
- 🎯 Intelligent file organization for both audio and transcripts
- ⚡ Quick and easy command-line interface
- 🎛️ Configurable microphone selection

## 🚀 Getting Started

### 📋 Prerequisites

- Python 3.9 or higher
- An OpenAI API key
- Obsidian vault set up on your system
- A working microphone

### 🛠️ Installation

1. Clone this repository:

```bash
git clone https://github.com/MiMa6/obsidian-automation.git
cd obsidian-automation
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-api-key-here
OBSIDIAN_VAULT_PATH=/path/to/your/vault
MICROPHONE_NAME=Your Microphone Name  # Optional: specify your preferred microphone
```

5. Config your microphone

Edit `src/audio_recorder.py`

```Python
DEFAULT_MIC_NAME = "For example External USB Microphone"
```

## 🎮 Usage

1. Run the script:

```bash
python speech_to_text.py
```

2. Choose your action:

   - Press `1` to start recording
   - Press `2` to quit

3. When recording:
   - Start speaking naturally
   - The recording will automatically stop after 2 seconds of silence
   - Your audio will be transcribed and saved to your Obsidian vault

## 📁 Project Structure

```
.
├── src/
│   ├── audio_recorder.py    # Handles voice recording
│   ├── transcriber.py       # Manages OpenAI transcription
│   ├── file_manager.py      # Handles file operations
│   └── __init__.py
├── speech_to_text.py        # Main script
├── requirements.txt
└── .env
```

## 🎯 How It Works

1. 🎤 **Recording**: Uses your configured microphone to capture audio
2. 🤖 **Processing**: Automatically detects silence to stop recording
3. ✨ **Transcription**: Sends audio to OpenAI's Whisper model for accurate transcription
4. 📝 **Organization**:
   - Transcripts go to `[vault]/Audios/SpeechToText/`
   - Original recordings move to `[vault]/Audios/Translated/`

## 🔧 Configuration

You can adjust these settings in `src/audio_recorder.py`:

- `SILENCE_THRESHOLD`: Sensitivity for silence detection (default: 0.02)
- `SILENCE_DURATION`: How long to wait in silence before stopping (default: 2.0 seconds)
- `MAX_DURATION`: Maximum recording duration (default: 300 seconds)
- `DEFAULT_MIC_NAME`: Default microphone to use if none specified
