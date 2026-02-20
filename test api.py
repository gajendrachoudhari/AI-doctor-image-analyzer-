import os
from dotenv import load_dotenv
import requests

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

print("=" * 50)
print("🔍 GROQ API TEST")
print("=" * 50)

# Check API key
if not GROQ_API_KEY:
    print("❌ ERROR: GROQ_API_KEY not found in .env file!")
    print("📝 Please create a .env file with: GROQ_API_KEY=your_key_here")
    exit(1)

print(f"✅ API Key found: {GROQ_API_KEY[:10]}...{GROQ_API_KEY[-5:]}")

# Test API connection
print("\n🔄 Testing API connection...")

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.2-11b-vision-instruct",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello, can you respond?"}
            ]
        }
    ],
    "max_tokens": 50
}

try:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json=payload,
        headers=headers,
        timeout=30
    )
    
    print(f"📡 Response Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API Connection Successful!")
        data = response.json()
        print(f"📝 Response: {data['choices'][0]['message']['content']}")
    else:
        print(f"❌ API Error: {response.status_code}")
        print(f"📝 Response: {response.text}")
        
except Exception as e:
    print(f"❌ Connection Error: {str(e)}")

print("\n" + "=" * 50)