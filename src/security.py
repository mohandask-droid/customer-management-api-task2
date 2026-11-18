import os
from dotenv import load_dotenv
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

load_dotenv()
API_KEY = os.getenv("API_KEY")


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(key: str = Security(api_key_header)):
    
    if not API_KEY or key != API_KEY:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or missing API key")