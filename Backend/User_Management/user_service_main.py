from fastapi import FastAPI, HTTPException, Depends, status
from schemas import UserCreate, UserLogin, UserOut
from auth import hash_password, verify_password, create_access_token, get_current_user
from database import get_user_by_email, create_user, get_all_users

app = FastAPI(title="User Management Service")

#Configuration
ALLOWED_DOMAIN = "@cybertribe.com" #Restrict registrations to this domain
COMPANY_REGISTRATION_KEY = "SecureTribe2025!" #Later move to env variable

@app.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    if not user.email.endswith(ALLOWED_DOMAIN):
        raise HTTPException(status_code=403, detail="Email domain not allowed")
    
    if user.secret_key != COMPANY_REGISTRATION_KEY:
        raise HTTPException(status_code=403, detail="Invalid registration key")
    
    existing = get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user.password)
    create_user(user.email, hashed_pw)
    token = create_access_token(user.email)

    return {"email": user.email, "token": token}

@app.post("/login", response_model=UserOut)
def login(user: UserLogin):
    db_user = get_user_by_email(user.email)

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(user.email)

    return {"email": user.email, "token": token}

@app.get("/users")
def list_users(current_user: str = Depends(get_current_user)):
    users = get_all_users()
    return {"requester": current_user, "registered_users": users}