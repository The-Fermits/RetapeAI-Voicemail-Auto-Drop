import os
import requests
from dotenv import load_dotenv

# Move up one level to find the .env file
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

GEMINI_KEY = os.getenv("GEMINI_API_KEY")

def test_gemini():
    if not GEMINI_KEY:
        print("❌ Error: GEMINI_API_KEY not found in .env")
        return

    print("🤖 Calling Gemini API...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    payload = {
        "contents": [{
            "parts": [{"text": "What is the capital of India?"}]
        }]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if response.status_code == 200:
            answer = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"🇮🇳 Gemini Answer: {answer}")
            print("✨ Gemini API is WORKING!")
        else:
            print(f"❌ API Error ({response.status_code}): {data.get('error', {}).get('message')}")
            
    except Exception as e:
        print(f"❌ Network Error: {e}")

if __name__ == "__main__":
    test_gemini()