import hashlib
import uuid
from fastapi import Request, HTTPException, Security, Depends, status
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db, hash_password
from app.models import AdminUser

# Session storage in memory
ACTIVE_SESSIONS = {}

cookie_sec = APIKeyCookie(name="admin_session", auto_error=False)

def create_session(username: str) -> str:
    token = str(uuid.uuid4())
    ACTIVE_SESSIONS[token] = username
    return token

def verify_session(token: str) -> bool:
    return token in ACTIVE_SESSIONS

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    # Check Cookie first, then Authorization Header
    token = request.cookies.get("admin_session")
    if not token:
        auth_hdr = request.headers.get("Authorization")
        if auth_hdr and auth_hdr.startswith("Bearer "):
            token = auth_hdr.split(" ")[1]
            
    if not token or token not in ACTIVE_SESSIONS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiyadan o'tilmagan. Iltimos, adminga kiring."
        )
    
    username = ACTIVE_SESSIONS[token]
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin foydalanuvchisi topilmadi."
        )
    return admin
