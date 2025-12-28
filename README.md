# 🤖 AI Voicemail Auto-Drop

An intelligent telephony automation tool designed to detect the end of a voicemail greeting and automatically "drop" a pre-recorded message. This project uses a **3-Tiered Detection Logic** to ensure high accuracy across different types of voicemail systems.

---

## 🛠 Project Architecture

The system is built with a modular structure to ensure scalability and clean code:

- **STT Engine:** Powered by **Deepgram Nova-2** for real-time, low-latency transcription via WebSockets.
- **LLM Intelligence:** Powered by **Gemini 2.5 Flash** to analyze linguistic intent.
- **Audio Management:** Uses `sounddevice` for streaming and `winsound` for native Windows audio playback (ensures 1:1 speed).

---

## 🚀 The 3-Tier Detection Logic

To solve the "When do I drop?" problem, the engine evaluates audio in three stages:

1. **Linguistic Intent (Tier 1):** The transcript is sent to Gemini AI. It identifies if the speaker has finished their intro or reached a "drop point" (e.g., after giving a name/number).
2. **Keyword & Silence (Tier 2):** Instant detection of trigger words like *"beep"*, *"tone"*, or *"message"* combined with a 3-second silence window.
3. **Physical Silence (Tier 3):** A hard 6-second silence safety net that triggers the drop even if the AI or keywords fail to recognize the context.

---

## 📁 File Structure

```text
voicemail-auto-drop/
├── run_detector.py          # Main entry point script
├── src/                     # Core Logic
│   ├── engine.py            # Decision engine & coordination
│   └── utils.py             # Logging & helper functions
├── scripts/                 # Utility scripts (TTS generation)
├── tests/                   # API verification scripts
└── assets/                  # Audio greetings & output payloads