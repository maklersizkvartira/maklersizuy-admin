import hashlib
import hmac
import time
import uuid
from fastapi import Request, HTTPException, Security, Depends, status
from fastapi.security import APIKeyCookie, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db, hash_password
from app.models import AdminUser

# Session storage in memory fallback
ACTIVE_SESSIONS = {}
SESSION_SECRET = "maklersiz-admin-secure-key-2026-uz"

cookie_sec = APIKeyCookie(name="admin_session", auto_error=False)

def create_session(username: str) -> str:
    ts = str(int(time.time()))
    payload = f"{username}:{ts}"
    sig = hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token = f"{payload}:{sig}"
    ACTIVE_SESSIONS[token] = username
    return token

def verify_and_get_username(token: str) -> str | None:
    if not token:
        return None
    if token in ACTIVE_SESSIONS:
        return ACTIVE_SESSIONS[token]
    try:
        parts = token.split(":")
        if len(parts) == 3:
            username, ts, sig = parts
            expected = hmac.new(SESSION_SECRET.encode(), f"{username}:{ts}".encode(), hashlib.sha256).hexdigest()
            if hmac.compare_digest(sig, expected):
                # 14 days validity
                if int(time.time()) - int(ts) < 86400 * 14:
                    ACTIVE_SESSIONS[token] = username
                    return username
    except Exception:
        pass
    return None

def verify_session(token: str) -> bool:
    return verify_and_get_username(token) is not None

def get_current_admin(request: Request, db: Session = Depends(get_db)):
    # Check Cookie first, then Authorization Header
    token = request.cookies.get("admin_session")
    if not token:
        auth_hdr = request.headers.get("Authorization")
        if auth_hdr and auth_hdr.startswith("Bearer "):
            token = auth_hdr.split(" ")[1]
            
    username = verify_and_get_username(token) if token else None
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autentifikatsiyadan o'tilmagan. Iltimos, adminga kiring."
        )
    
    admin = db.query(AdminUser).filter(AdminUser.username == username).first()
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin foydalanuvchisi topilmadi."
        )
    return admin

