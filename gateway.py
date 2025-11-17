# gateway.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
from fastapi.middleware.cors import CORSMiddleware

# --- Configuration ---
USER_SERVICE_URL = "http://127.0.0.1:8001"
# httpx client for making async requests
http_client = None

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or replace with specific URL: ["http://127.0.0.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Event Handlers for httpx lifecycle ---

@app.on_event("startup")
async def startup_event():
    global http_client
    http_client = httpx.AsyncClient(base_url=USER_SERVICE_URL)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

# --- Gateway Routes ---

# 1. Registration Route
@app.post("/api/v1/users/register")
async def register_user(request: Request):
    try:
        # Get the request body (UserCreate payload)
        body = await request.json()
        
        # Forward the request to the User Management Service's /register endpoint
        response = await http_client.post("/register", json=body)
        
        # If the backend responded successfully (e.g., 200, 201)
        if response.is_success:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        
        # If the backend returned an error (e.g., 400, 404, 500)
        else:
            # Re-raise the HTTPException from the backend
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error from user service"))
            
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User Service is unavailable")
    except Exception as e:
        # Catch other potential errors (like JSON parsing)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

# 2. Login Route (Similar to Registration)
@app.post("/api/v1/users/login")
async def login_user(request: Request):
    try:
        body = await request.json()
        response = await http_client.post("/login", json=body)
        
        if response.is_success:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error from user service"))
            
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User Service is unavailable")

# 3. List Users Route (GET Request)
@app.get("/api/v1/users/list")
async def list_registered_users():
    try:
        # Forward the GET request to the User Management Service's /users endpoint
        response = await http_client.get("/users")
        
        if response.is_success:
            return JSONResponse(content=response.json(), status_code=response.status_code)
        else:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Error from user service"))
            
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="User Service is unavailable")