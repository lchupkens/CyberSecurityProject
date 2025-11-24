from fastapi import FastAPI, HTTPException, Depends
from schemas import UserCreate, UserLogin, UserOut
from auth import hash_password, verify_password, create_access_token, get_current_user
from models import fake_users_db

app = FastAPI(title="User Management Service")

@app.post("/register", response_model=UserOut)
def register(user: UserCreate):
    if user.email in fake_users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pw = hash_password(user.password)
    fake_users_db[user.email] = hashed_pw
    token = create_access_token(user.email)
    return {"email": user.email, "token": token}

@app.post("/login", response_model=UserOut)
def login(user: UserLogin):
    stored_pw = fake_users_db.get(user.email)
    if not stored_pw or not verify_password(user.password, stored_pw):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.email)
    return {"email": user.email, "token": token}

@app.get("/users")
def list_users(current_user: str = Depends(get_current_user)):
    return {"registered_users": list(fake_users_db.keys()), "requester": current_user}