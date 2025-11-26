from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from easynmt import EasyNMT
import nltk
import html
from cache_db import get_cached_translation, save_translation

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')

app = FastAPI(title="Machine Translation Service")

#Load model
print("Loading translation model...")
model = EasyNMT('m2m_100_418M')
print("Model loaded successfully.")

#Pydantic model
class Translationrequest(BaseModel):
    user_id: str
    text: str
    target_lang: str = "nl"

#API endpoint
@app.post("/translate")
async def translate(request: Translationrequest):
    try:
        cached_text = get_cached_translation(request.user_id, request.text, request.target_lang)

        if cached_text:
            print(f"Cache hit for user {request.user_id}")
            return {"translation": html.escape(cached_text), "source": "cache"}
        
        print("No cached translation found, proceeding to translate...")
        
        translation = model.translate(request.text, source_lang= 'en', target_lang=request.target_lang)

        sanitized_translation = html.escape(translation)

        save_translation(request.user_id, request.text, request.target_lang, sanitized_translation)

        return {"translation": sanitized_translation, "source": "model"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")