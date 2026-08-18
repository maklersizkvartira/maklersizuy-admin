import json
import random
import hashlib
import os
import tempfile
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, AdminUser, User, Listing, TrafficMetric, Report, Verification

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

        if not db.query(Report).first():
            reports = [
                Report(
                    listing_title="Chilonzor 7-havze 2 xonali kvartira",
                    reporter_name="Shoxrux Abdullayev",
                    reporter_phone="+998 90 999 11 22",
                    reason_label="Rieltorlik / Makler xizmati",
                    details="Uy egasiman deb yozgan, lekin tel qilsam 15% maklerlik haqi so'radi.",
                    status="PENDING"
                ),
                Report(
                    listing_title="Yunusobod 11-kvartal 3 xonali shinam xonadon",
                    reporter_name="Kamola Xasanova",
                    reporter_phone="+998 91 555 44 33",
                    reason_label="Soxta rasm / Dublikat",
                    details="Ushbu e'londagi rasmlar OLX dagi boshqa makler e'lonidan ko'chirib olingan.",
                    status="PENDING"
                ),
                Report(
                    listing_title="Mirzo Ulug'bek metrosi yonida 2 xona",
                    reporter_name="Jasur Mirzayev",
                    reporter_phone="+998 93 111 00 99",
                    reason_label="Noto'g'ri narx ko'rsatilgan",
                    details="E'londa 320$ deb yozilgan, javob bergan odam 450$ narx aytdi.",
                    status="RESOLVED"
                )
            ]
            db.add_all(reports)
            db.commit()
            print("Default sample reports created.")

        if not db.query(Verification).first():
            verifications = [
                Verification(
                    user_name="Jasur Karimov",
                    user_phone="+998 90 123 45 67",
                    level=4,
                    trust_score=98,
                    passport_image="https://images.unsplash.com/photo-1544717305-2782549b5136?w=600&auto=format&fit=crop&q=60",
                    selfie_image="https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=60",
                    cadastre_code="10:01:04:02:01:0045",
                    status="PENDING"
                ),
                Verification(
                    user_name="Azizbek Raximov",
                    user_phone="+998 90 123 45 67",
                    level=4,
                    trust_score=95,
                    passport_image="https://images.unsplash.com/photo-1544717305-2782549b5136?w=600&auto=format&fit=crop&q=60",
                    selfie_image="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600&auto=format&fit=crop&q=60",
                    cadastre_code="10:05:08:03:02:0112",
                    status="APPROVED"
                ),
                Verification(
                    user_name="Malika Shodieva",
                    user_phone="+998 91 222 33 44",
                    level=3,
                    trust_score=92,
                    passport_image="https://images.unsplash.com/photo-1544717305-2782549b5136?w=600&auto=format&fit=crop&q=60",
                    selfie_image="https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=600&auto=format&fit=crop&q=60",
                    cadastre_code="10:03:02:01:04:0078",
                    status="PENDING"
                )
            ]
            db.add_all(verifications)
            db.commit()
            print("Default verifications created.")
    except Exception as e:
        db.rollback()
        print("Database initialization error:", e)
    finally:
        db.close()
