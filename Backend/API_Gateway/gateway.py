from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

#Configuration
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://127.0.0.1:8001")
TRANSLATION_SERVICE_URL = os.getenv("TRANSLATION_SERVICE_URL", "http://127.0.0.1:8002")

#httpx client for making async requests
http_client = None

#Lifespan Manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    global http_client
    http_client = httpx.AsyncClient()
    print("Gatway: HTTP Client connection opened.")
    yield

    await http_client.aclose()
    print("Gateway: HTTP Client connection closed.")

app = FastAPI(title="API Gateway", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#All Gateway Routes

#Registration Route
@app.post("/api/v1/users/register")
async def register_user(request: Request):
    try:
        #Get the request body (UserCreate payload)
        body = await request.json()
        
        #Forward the request to the User Management Service's /register endpoint
        response = await http_client.post(f"{USER_SERVICE_URL}/register", json=body)
        
        #If success or if it's a 422 (Validation Error) or 400 (Bad Request)
        if response.is_success or response.status_code in [400, 422]:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        
        #For other errors (500s)
        else:
            #Re-raise the HTTPException from the backend
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error from user service"))
            
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User Service is unavailable")
    except Exception as e:
        #Catch other potential errors (like JSON parsing)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

#Login Route (Similar to Registration)
@app.post("/api/v1/users/login")
async def login_user(request: Request):
    try:
        body = await request.json()
        response = await http_client.post(f"{USER_SERVICE_URL}/login", json=body)
        
        if response.is_success:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error from user service"))
            
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User Service is unavailable")

#List Users Route (GET Request)
@app.get("/api/v1/users/list")
async def list_registered_users(request: Request):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
             raise HTTPException(status_code=401, detail="Authorization header missing")
        headers = {"Authorization": auth_header} 
        response = await http_client.get(f"{USER_SERVICE_URL}/users", headers=headers)
        if response.is_success:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error from user service"))        
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User Service is unavailable")
    
#Translation Route
@app.post("/api/v1/translate")
async def translate_text(request: Request):

    #1. Security check
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    content_length = request.headers.get("content-length")
    MAX_BYTES = 2 * 1024 * 1024  #2 MB limit
    if content_length and int(content_length) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Payload too large. Maximum size is 2 MB.")

    try:
        #2. Identity Verification
        user_response = await http_client.get(f"{USER_SERVICE_URL}/users", headers={"Authorization": auth_header})

        if not user_response.is_success:
            raise HTTPException(status_code=user_response.status_code, detail="Invalid or Expired Token")
        
        user_data = user_response.json()
        user_email = user_data.get("requester")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth Check Failed: {str(e)}")
    
    #3. The Translation
    try:
        body = await request.json()

        payload = {"text": body.get("text"), "target_lang": body.get("target_lang", "nl"), "user_id": user_email}

        response = await http_client.post(f"{TRANSLATION_SERVICE_URL}/translate", json=payload, timeout=60.0)
        
        return JSONResponse(content=response.json(), status_code=response.status_code)
    
    #4. Handle Connection Errors
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Translation Service is unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation Error: {str(e)}")