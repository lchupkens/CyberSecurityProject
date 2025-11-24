from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from easynmt import EasyNMT
import difflib
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

app = FastAPI(title="Machine Translation Service")

#Load model
print("Loading translation model...")
model = EasyNMT('m2m_100_418M')
print("Model loaded successfully.")

#Cache
translation_cache = {}

#Pydantic model
class Translationrequest(BaseModel):
    user_id: str
    text: str
    target_lang: str = "nl"

#Helper functions
def get_similar_cached(user_id, text, target_lang, threshold=0.98):
    #Check if user exists
    if user_id not in translation_cache:
        return None
    
    #Check if target language exists for user
    if target_lang not in translation_cache[user_id]:
        return None
    
    best_ratio = 0
    best_key = None

    for cached_sentence in translation_cache[user_id][target_lang]:
        ratio = difflib.SequenceMatcher(None, text, cached_sentence).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_key = cached_sentence

    if best_ratio >= threshold:
        return best_key, translation_cache[user_id][target_lang][best_key]

    return None

def update_cache(user_id, text, target_lang, translation):
    if user_id not in translation_cache:
        translation_cache[user_id] = {}

    if target_lang not in translation_cache[user_id]:
        translation_cache[user_id][target_lang] = {}

    translation_cache[user_id][target_lang][text] = translation

#API endpoint
@app.post("/translate")
async def translate(request: Translationrequest):
    try:
        match = get_similar_cached(request.user_id, request.text, request.target_lang)

        if match:
            print(f"Cache hit for user {request.user_id} ({request.target_lang})")
            return {"translation": match[1], "source": "cache"}
        
        print(f"Cache miss for user {request.user_id}, translating to {request.target_lang}...")
        translation = model.translate(request.text, source_lang='en', target_lang=request.target_lang)

        update_cache(request.user_id, request.text, request.target_lang, translation)
        return {"translation": translation, "source": "model"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")