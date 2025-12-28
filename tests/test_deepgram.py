import os
import wave
import asyncio
import websockets
import json
from dotenv import load_dotenv

# Move up one level to find the .env file if running from the tests folder
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

DEEPGRAM_KEY = os.getenv("DEEPGRAM_API_KEY")
# Adjust path to your test audio file
TEST_WAV = os.path.join(os.path.dirname(__file__), '..', 'assets', 'greetings', 'audio1.wav')

async def test_dg():
    if not DEEPGRAM_KEY:
        print("❌ Error: DEEPGRAM_API_KEY not found in .env")
        return

    url = "wss://api.deepgram.com/v1/listen?model=nova-2&encoding=linear16&sample_rate=8000"
    headers = {"Authorization": f"Token {DEEPGRAM_KEY}"}

    print(f"📡 Connecting to Deepgram...")
    try:
        async with websockets.connect(url, additional_headers=headers) as ws:
            print("✅ Connected successfully!")
            
            with wave.open(TEST_WAV, "rb") as wf:
                print(f"🎙️ Streaming {TEST_WAV}...")
                data = wf.readframes(4000)
                await ws.send(data)
                
            # Wait for a transcript response
            response = await ws.recv()
            res_json = json.loads(response)
            transcript = res_json.get("channel", {}).get("alternatives", [{}])[0].get("transcript", "")
            
            if transcript:
                print(f"🗣️  Deepgram Transcript: {transcript}")
                print("✨ Deepgram API is WORKING!")
            else:
                print("⚠️  Connected, but no transcript received. Check if audio1.wav has speech.")
                
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_dg())