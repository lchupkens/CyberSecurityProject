from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from easynmt import EasyNMT
import nltk
import html
import difflib
from cache_db import save_translation, get_all_user_translations

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

def find_best_match(user_id, current_text, target_lang, threshold=0.98):
    history = get_all_user_translations(user_id, target_lang)
    if not history:
        return None
    
    best_ratio = 0
    best_translation = None

    for entry in history:
        cached_source = entry["source_text"]
        cached_translation = entry["translated_text"]
        
        ratio = difflib.SequenceMatcher(None, current_text, cached_source).ratio()

        if ratio > best_ratio:
            best_ratio = ratio
            best_translation = cached_translation

    if best_ratio >= threshold:
        return best_translation
    return None

#API endpoint
@app.post("/translate")
async def translate(request: Translationrequest):
    try:
        clean_text = request.text.strip()

        if not clean_text:
            raise HTTPException(status_code=400, detail="Input text is empty.")

        cached_text = find_best_match(request.user_id, clean_text, request.target_lang, threshold=0.98)

        if cached_text:
            print(f"Cache hit (fuzzy) for user {request.user_id}")
            return {"translation": html.escape(cached_text), "source": "cache"}
        
        print("No cached translation found, proceeding to translate...")
        
        translation = model.translate(clean_text, source_lang= 'en', target_lang=request.target_lang)

        sanitized_translation = html.escape(translation)

        save_translation(request.user_id, clean_text, request.target_lang, sanitized_translation)

        return {"translation": sanitized_translation, "source": "model"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")