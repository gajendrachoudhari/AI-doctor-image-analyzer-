from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import base64
import requests
from dotenv import load_dotenv
import os
import logging
import json
import re
from urllib.parse import quote_plus

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

app = FastAPI()

# CRITICAL: Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

@app.get("/")
async def root():
    return {"status": "AI-DOCTOR API is running", "version": "1.0"}

@app.post("/upload_and_query")
async def upload_and_query(image: UploadFile = File(...), query: str = Form(...)):
    if not GROQ_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY is missing. Add it to your .env file."
        )
    logger.info(f"📥 Received query: {query}")
    logger.info(f"📥 Received image: {image.filename}")
    
    # Read image
    img_bytes = await image.read()
    if not img_bytes:
        raise HTTPException(status_code=400, detail="Empty image file")

    # Convert to Base64
    encoded = base64.b64encode(img_bytes).decode()
    
    # Detect MIME type
    filename_lower = image.filename.lower()
    if filename_lower.endswith(".png"):
        mime = "image/png"
    elif filename_lower.endswith((".jpg", ".jpeg")):
        mime = "image/jpeg"
    else:
        mime = "image/jpeg"  # Default

    logger.info(f"🖼️ Image type: {mime}")

    def ask_groq(model_name, prompt_text=None):
        """Call Groq Vision API with correct format. prompt_text defaults to user query."""
        if prompt_text is None:
            prompt_text = query
        payload = {
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime};base64,{encoded}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            logger.info(f"🤖 Calling {model_name}...")
            
            response = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
            
            logger.info(f"📡 Response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"API Error {response.status_code}: {response.text}"
                logger.error(error_msg)
                return f"❌ {error_msg}"
            
            data = response.json()
            
            # Extract response
            if "choices" in data and len(data["choices"]) > 0:
                result = data["choices"][0]["message"]["content"]
                logger.info(f"✅ {model_name} responded successfully")
                return result
            else:
                logger.error(f"Unexpected API response format: {data}")
                return "❌ Unexpected API response format"
            
        except requests.exceptions.Timeout:
            logger.error(f"Timeout calling {model_name}")
            return "❌ Request timeout - API took too long to respond"
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error calling {model_name}: {str(e)}")
            return f"❌ Network error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error calling {model_name}: {str(e)}")
            return f"❌ Error: {str(e)}"

    # Groq vision models (see https://console.groq.com/docs/vision)
    MODEL_SCOUT = "meta-llama/llama-4-scout-17b-16e-instruct"
    MODEL_MAVERICK = "meta-llama/llama-4-maverick-17b-128e-instruct"

    logger.info("🔄 Starting analysis (Analyzer)...")
    result_scout = ask_groq(MODEL_SCOUT, query)
    logger.info("🔄 Starting Exercises (yoga & exercise)...")
    exercise_prompt = "Based on this medical image, suggest suitable yoga poses and exercises. List them pointwise. Also mention any precautions if relevant."
    result_maverick = ask_groq(MODEL_MAVERICK, exercise_prompt)
    logger.info("✅ Analysis complete!")

    # --- Medicine recommendations & home remedies (text model) ---
    def get_recommendations(analysis1: str, analysis2: str) -> dict:
        """Call Groq text model to get medicines and home remedies from analysis."""
        prompt = f"""Based on the following medical image analyses, suggest:
1) Recommended medicines: list only generic/medicine names (e.g. Paracetamol, Ibuprofen, Cetirizine). Use 3-6 items.
2) Home remedies: a list of safe, practical home care tips as separate points (pointwise).

Reply with ONLY valid JSON, no other text:
{{"medicines": ["Medicine1", "Medicine2", ...], "home_remedies": ["First point.", "Second point.", "Third point.", ...]}}

Analysis from analyzer:
{analysis1[:2000]}

Exercises/yoga from second model:
{analysis2[:2000]}
"""
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 800,
            "temperature": 0.3,
        }
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        try:
            r = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=45)
            if r.status_code != 200:
                return {"medicines": [], "home_remedies": []}
            text = r.json()["choices"][0]["message"]["content"]
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                data = json.loads(json_match.group())
                medicines = data.get("medicines", [])
                if isinstance(medicines, str):
                    medicines = [m.strip() for m in medicines.split(",")] if medicines else []
                hr = data.get("home_remedies", [])
                if isinstance(hr, str):
                    hr = [s.strip() for s in hr.split("\n") if s.strip()] if hr else []
                if not isinstance(hr, list):
                    hr = []
                return {
                    "medicines": medicines if isinstance(medicines, list) else [],
                    "home_remedies": hr,
                }
        except Exception as e:
            logger.warning(f"Recommendations parse error: {e}")
        return {"medicines": [], "home_remedies": []}

    def build_buy_links(medicines: list) -> list:
        """Build where-to-buy links for each medicine (1mg, PharmEasy, Netmeds)."""
        links_list = []
        for name in medicines:
            if not name or not isinstance(name, str):
                continue
            q = quote_plus(name.strip())
            links_list.append({
                "name": name.strip(),
                "1mg": f"https://www.1mg.com/search?name={q}",
                "pharmeasy": f"https://www.pharmeasy.com/search/all?name={q}",
                "netmeds": f"https://www.netmeds.com/catalogsearch/result?q={q}",
            })
        return links_list

    rec = get_recommendations(result_scout, result_maverick)
    buy_links = build_buy_links(rec["medicines"])

    return {
        "llama_scout": result_scout,
        "llama_maverick": result_maverick,
        "medicines": rec["medicines"],
        "home_remedies": rec["home_remedies"],
        "buy_links": buy_links,
    }

# Run with: uvicorn app:app --reload --host 0.0.0.0 --port 8007