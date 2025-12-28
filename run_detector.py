import os
import asyncio
from dotenv import load_dotenv
from src.engine import VoicemailEngine

load_dotenv()

config = {
    'dg_key': os.getenv("DEEPGRAM_API_KEY"),
    'gemini_key': os.getenv("GEMINI_API_KEY"),
    'input_wav': "assets/greetings/audio1.wav",
    'output_wav': "assets/outputs/msg_audio.wav"
}

if __name__ == "__main__":
    asyncio.run(VoicemailEngine(config).run())