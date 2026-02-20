import base64
import requests
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing in .env")


def process_image(image_path, query):
    """
    Process an image with Groq Vision API
    
    Args:
        image_path: Path to the image file
        query: Question to ask about the image
    
    Returns:
        Dictionary with responses from both models
    """
    try:
        # Read image bytes
        with open(image_path, "rb") as img:
            image_bytes = img.read()

        # Encode Base64
        encoded_image = base64.b64encode(image_bytes).decode()

        # Detect file type
        mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

        def ask_groq(model):
            """Call Groq API with correct message format"""
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": query},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime};base64,{encoded_image}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 400
            }

            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json",
            }

            res = requests.post(GROQ_API_URL, json=payload, headers=headers)

            if res.status_code != 200:
                return f"Error {res.status_code}: {res.text}"

            return res.json()["choices"][0]["message"]["content"]

        # Call both models
        return {
            "llama_11b": ask_groq("llama-3.2-11b-vision-instruct"),
            "llama_90b": ask_groq("llama-3.2-90b-vision-instruct"),
        }

    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Test the function
    out = process_image("test1.png", "What is in this image?")
    print("=== Llama 11B Response ===")
    print(out.get("llama_11b", "No response"))
    print("\n=== Llama 90B Response ===")
    print(out.get("llama_90b", "No response"))
    if "error" in out:
        print(f"\n❌ ERROR: {out['error']}")