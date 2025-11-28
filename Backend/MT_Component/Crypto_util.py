import os
from cryptography.fernet import Fernet

CRYPTO_KEY = os.getenv("CRYPTO_KEY")

if not CRYPTO_KEY:
    raise ValueError("CRYPTO_KEY environment variable is not set.")

f = Fernet(CRYPTO_KEY.encode())

def encrypt_data(data: str) -> str:
    if not data:
        return ""
    token = f.encrypt(data.encode())
    return token.decode()

def decrypt_data(token: str) -> str:
    if not token:
        return ""
    data = f.decrypt(token.encode())
    return data.decode()