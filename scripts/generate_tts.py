import requests

# Your Clearpath Finance compliant script
MESSAGE_TEXT = (
    "Hello, this is a message from Clearpath Finance regarding your recent inquiry. "
    "Please call us back at 1-800-555-0199 at your earliest convenience. Thank you."
)

def generate_msg():
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" # 'Rachel' voice
    headers = {"xi-api-key": "YOUR_ELEVENLABS_KEY"}
    data = {"text": MESSAGE_TEXT, "model_id": "eleven_monolingual_v1"}
    
    response = requests.post(url, json=data, headers=headers)
    with open("msg_audio.wav", "wb") as f:
        f.write(response.content)
    print("✅ msg_audio.wav generated.")