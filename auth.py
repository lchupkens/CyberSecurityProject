from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta


SECRET_KEY = "supersecretkey" #Must be replaced later on with an environmental variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    truncated = password[:72]
    return pwd_context.hash(truncated)

def verify_password(plain_password: str, hashed_password: str):
    truncated = plain_password[:72]
    return pwd_context.verify(truncated, hashed_password)

def create_access_token(user_email: str):
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user_email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)