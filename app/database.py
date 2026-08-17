import json
import random
import hashlib
import os
import tempfile
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, AdminUser, User, Listing, TrafficMetric

if os.environ.get("VERCEL") or not os.access(".", os.W_OK):
    db_path = os.path.join(tempfile.gettempdir(), "maklersiz_admin.db")
else:
    db_path = "./maklersiz_admin.db"

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_path}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db_and_seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # Check if admin user exists, if not create default admin
        if not db.query(AdminUser).first():
            admin = AdminUser(
                username="admin",
                password_hash=hash_password("admin123"),
                full_name="Bosh Admin (Maklersiz.uz)"
            )
            db.add(admin)
            db.commit()
            print("Default admin user created successfully.")
    except Exception as e:
        db.rollback()
        print("Database initialization error:", e)
    finally:
        db.close()
