import asyncio
import websockets
import json
import wave
import requests
import time
import winsound
import numpy as np
import sounddevice as sd
from concurrent.futures import ThreadPoolExecutor
from src.utils import ts_log

class VoicemailEngine:
    def __init__(self, config):
        self.dg_key = config['dg_key']
        self.gemini_key = config['gemini_key']
        self.input_wav = config['input_wav']
        self.output_wav = config['output_wav']
        
        # Exact same global state from your original code
        self.last_speech_time = time.time()
        self.full_transcript_list = [] # Reverted to your original naming
        self.is_voicemail_dropped = False # Reverted naming
        self.processing_gemini = False
        self.executor = ThreadPoolExecutor(max_workers=1)

    def ask_gemini(self, transcript):
        """Logic copied exactly from your original provided code"""
        ts_log(f"🤖 Calling Gemini with: \"{transcript}\"")
        prompt_text = (
            f"Transcript: \"{transcript}\".\n\n"
            "Identify if this voicemail greeting seems like it has reached its 'Message Drop Point' and we can leave a message.\n"
            "some Criteria for 'Yes':\n"
            "1. The speaker explicitly asks to leave a message (e.g., 'Leave a message', 'Record your speech').\n"
            "2. The speaker mentions the beep or tone (e.g., 'At the tone', 'After the beep').\n"
            "3. The transcript ends with a name , contact number or extension.\n"
            "Answer 'Yes' or 'No' only. Prefer to say 'Yes'in case of ambiguity"
        )
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_key}"
        try:
            r = requests.post(url, json={"contents": [{"parts": [{"text": prompt_text}]}]}, timeout=9)
            data = r.json()
            if "candidates" in data:
                result = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                ts_log(f"🤖 Gemini Verdict: {result}")
                return result
            else:
                msg = data.get("error", {}).get("message", "Unknown API error")
                ts_log(f"⚠️ Gemini API Warning: {msg}")
                return "No"
        except Exception as e:
            ts_log(f"❌ Gemini Network Error: {e}")
            return "No"

    async def drop_voicemail(self):
        """Logic copied exactly from your original winsound code"""
        if self.is_voicemail_dropped: return
        self.is_voicemail_dropped = True
        
        ts_log(f"🚀 [DROP START]")
        try:
            winsound.PlaySound(self.output_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
            await asyncio.sleep(13) 
            ts_log("✅ Drop Complete.")
        except Exception as e:
            ts_log(f"❌ Drop Error: {e}")

    async def run(self):
        wf = wave.open(self.input_wav, "rb")
        sr, ch = wf.getframerate(), wf.getnchannels()
        output_stream = sd.OutputStream(samplerate=sr, channels=ch, dtype='int16')
        output_stream.start()

        headers = {"Authorization": f"Token {self.dg_key}"}
        url = "wss://api.deepgram.com/v1/listen?model=nova-2&encoding=linear16&sample_rate=8000&channels=2&interim_results=true"
        
        async with websockets.connect(url, additional_headers=headers) as ws:
            self.last_speech_time = time.time()
            ts_log("📡 Stream Started")

            async def sender():
                while not self.is_voicemail_dropped:
                    data = wf.readframes(1024)
                    if not data: break
                    arr = np.frombuffer(data, dtype=np.int16).reshape(-1, ch)
                    output_stream.write(np.ascontiguousarray(arr))
                    await ws.send(data)
                    await asyncio.sleep(1024/sr)

            async def receiver():
                try:
                    async for msg in ws:
                        if self.is_voicemail_dropped: break
                        res = json.loads(msg)
                        if "channel" in res:
                            transcript = res["channel"]["alternatives"][0]["transcript"]
                            if transcript:
                                self.last_speech_time = time.time()
                                if res.get("is_final"):
                                    ts_log(f"🗣️  STT: {transcript}")
                                    self.full_transcript_list.append(transcript)
                except Exception:
                    pass # Prevent crash on connection close

            async def monitor():
                keywords = ["message", "tone", "beep", "record", "after the"]
                
                while not self.is_voicemail_dropped:
                    await asyncio.sleep(0.5)
                    
                    # Calculate current silence duration
                    silence = time.time() - self.last_speech_time
                    combined_text = " ".join(self.full_transcript_list).lower()

                    # ---------------------------------------------------------
                    # TIER 1: Gemini AI Logic (with Interruption Check)
                    # ---------------------------------------------------------
                    if self.full_transcript_list and not self.processing_gemini and silence >= 0.8:
                        # 1. Capture the state of silence BEFORE the API call
                        pre_gemini_speech_time = self.last_speech_time
                        
                        self.processing_gemini = True
                        loop = asyncio.get_running_loop()
                        
                        # 2. Call Gemini in the background
                        verdict = await loop.run_in_executor(self.executor, self.ask_gemini, combined_text)
                        
                        self.processing_gemini = False

                        # 3. THE INTERRUPTION CHECK:
                        # If self.last_speech_time changed while we were waiting for Gemini,
                        # it means the receiver() heard new speech.
                        if self.last_speech_time > pre_gemini_speech_time:
                            ts_log("🛑 User interrupted Gemini! Aborting drop to continue listening.")
                            continue 

                        # 4. If silence was maintained, act on the verdict
                        if "Yes" in verdict:
                            await self.drop_voicemail()
                            break

                    # ---------------------------------------------------------
                    # TIER 2 & 3: Safety Fallbacks
                    # ---------------------------------------------------------
                    if not self.processing_gemini:
                        # Keyword + 3s Silence
                        if any(k in combined_text for k in keywords) and silence >= 3.0:
                            ts_log("🎯 Safety Trigger: Keywords + 3s Silence")
                            await self.drop_voicemail()
                            break

                        # 6s Hard Silence (Ultimate safety net)
                        if silence >= 6.0:
                            ts_log("⚠️ Safety Trigger: 6s Hard Silence")
                            await self.drop_voicemail()
                            break

            await asyncio.gather(sender(), receiver(), monitor(), return_exceptions=True)
            output_stream.stop()
            wf.close()