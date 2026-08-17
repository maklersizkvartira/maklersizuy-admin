from fastapi import FastAPI, Depends, HTTPException, status, Response, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List
import json

from app.database import get_db, init_db_and_seed, hash_password
from app.models import AdminUser, User, Listing, TrafficMetric
from app.schemas import (
    LoginRequest, LoginResponse, ListingStatusUpdate,
    ListingFeaturedUpdate, UserStatusUpdate, UserTrustScoreUpdate,
    DashboardStatsResponse, UserCreate, UserUpdate, ListingCreate, ListingUpdate
)
from app.auth import create_session, ACTIVE_SESSIONS, get_current_admin

app = FastAPI(
    title="Maklersiz.uz Professional Admin Panel API",
    description="To'liq boshqaruv paneli va AI moderatsiya tizimi",
    version="1.0.0"
)

# Enable CORS for file:// and cross-origin access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    init_db_and_seed()

# Serve main Dashboard Web App
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# Authentication Endpoints
@app.post("/api/auth/login")
def login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    admin = db.query(AdminUser).filter(AdminUser.username == data.username).first()
    if not admin or admin.password_hash != hash_password(data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login yoki parol xato kiritildi!"
        )
    
    token = create_session(admin.username)
    response.set_cookie(
        key="admin_session",
        value=token,
        httponly=True,
        max_age=86400 * 7,
        samesite="lax"
    )
    return {
        "status": "success",
        "token": token,
        "username": admin.username,
        "full_name": admin.full_name
    }

@app.post("/api/auth/logout")
def logout(request: Request, response: Response):
    token = request.cookies.get("admin_session")
    if token and token in ACTIVE_SESSIONS:
        del ACTIVE_SESSIONS[token]
    response.delete_cookie("admin_session")
    return {"status": "logged_out"}

@app.get("/api/auth/me")
def get_me(admin: AdminUser = Depends(get_current_admin)):
    return {
        "username": admin.username,
        "full_name": admin.full_name
    }

# 📊 Analytics & Dashboard Stats
@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db), admin: AdminUser = Depends(get_current_admin)):
    metrics = db.query(TrafficMetric).order_by(TrafficMetric.date.asc()).all()
    traffic_history = [
        {
            "date": m.date,
            "daily_visitors": m.daily_visitors,
            "searches": m.total_searches,
            "new_listings": m.new_listings_count,
            "ai_approved": m.ai_auto_approved,
            "ai_flagged": m.ai_flagged
        } for m in metrics
    ]

    total_visitors_latest = metrics[-1].daily_visitors if metrics else 2150
    total_owners = db.query(User).filter(User.role == "OWNER").count()
    active_owners = db.query(User).filter(User.role == "OWNER", User.status == "ACTIVE").count()
    
    total_students = db.query(User).filter(User.role == "STUDENT").count()
    active_students = db.query(User).filter(User.role == "STUDENT", User.status == "ACTIVE").count()

    total_listings = db.query(Listing).count()
    approved_listings = db.query(Listing).filter(Listing.status == "APPROVED").count()
    blocked_listings = db.query(Listing).filter(Listing.status == "REJECTED").count()
    under_review_listings = db.query(Listing).filter(Listing.status == "UNDER_REVIEW").count()

    ai_auto_approved = sum(m.ai_auto_approved for m in metrics)
    ai_rejected_count = blocked_listings
    admin_unblocked_count = db.query(Listing).filter(Listing.status == "APPROVED", Listing.ai_risk_score >= 50).count()

    return {
        "daily_visitors": total_visitors_latest,
        "total_owners": total_owners,
        "active_owners": active_owners,
        "total_students": total_students,
        "active_students": active_students,
        "total_listings": total_listings,
        "approved_listings": approved_listings,
        "blocked_listings": blocked_listings,
        "under_review_listings": under_review_listings,
        "ai_auto_approved": ai_auto_approved,
        "ai_rejected_count": ai_rejected_count,
        "admin_unblocked_count": admin_unblocked_count,
        "traffic_history": traffic_history
    }

# 🚀 Listings Endpoints
@app.get("/api/listings")
def get_listings(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    query = db.query(Listing)

    if status_filter and status_filter != "ALL":
        query = query.filter(Listing.status == status_filter)
    
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Listing.title.ilike(search_pattern)) | 
            (Listing.description.ilike(search_pattern)) |
            (Listing.district.ilike(search_pattern))
        )

    listings = query.order_by(Listing.created_at.desc()).all()
    
    result = []
    for item in listings:
        owner = db.query(User).filter(User.id == item.owner_id).first()
        images_list = []
        try:
            images_list = json.loads(item.images) if item.images else []
        except:
            images_list = []

        result.append({
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "price": item.price,
            "price_period": item.price_period,
            "region": item.region,
            "district": item.district,
            "category": item.category,
            "room_count": item.room_count,
            "status": item.status,
            "is_featured": item.is_featured,
            "ai_risk_score": item.ai_risk_score,
            "ai_reject_reason": item.ai_reject_reason,
            "created_at": item.created_at.isoformat() if item.created_at else None,
            "images": images_list,
            "owner": {
                "id": owner.id if owner else None,
                "full_name": owner.full_name if owner else "Noma'lum",
                "phone": owner.phone if owner else "—",
                "trust_score": owner.trust_score if owner else 0,
                "status": owner.status if owner else "ACTIVE"
            }
        })
    return result

@app.post("/api/listings")
def create_listing(
    payload: ListingCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    owner = db.query(User).filter(User.id == payload.owner_id).first()
    if not owner:
        raise HTTPException(status_code=400, detail="Ko'rsatilgan foydalanuvchi/uy egasi topilmadi")

    images_json = json.dumps(payload.images) if payload.images else "[]"
    
    new_listing = Listing(
        title=payload.title,
        description=payload.description,
        price=payload.price,
        price_period=payload.price_period,
        region=payload.region,
        district=payload.district,
        category=payload.category,
        room_count=payload.room_count,
        images=images_json,
        owner_id=payload.owner_id,
        status=payload.status,
        is_featured=payload.is_featured,
        ai_risk_score=payload.ai_risk_score,
        ai_reject_reason=payload.ai_reject_reason
    )
    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)
    return {"status": "created", "listing_id": new_listing.id}

@app.put("/api/listings/{listing_id}")
def update_listing(
    listing_id: int,
    payload: ListingUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")

    if payload.title is not None: listing.title = payload.title
    if payload.description is not None: listing.description = payload.description
    if payload.price is not None: listing.price = payload.price
    if payload.price_period is not None: listing.price_period = payload.price_period
    if payload.region is not None: listing.region = payload.region
    if payload.district is not None: listing.district = payload.district
    if payload.category is not None: listing.category = payload.category
    if payload.room_count is not None: listing.room_count = payload.room_count
    if payload.images is not None: listing.images = json.dumps(payload.images)
    if payload.status is not None: listing.status = payload.status
    if payload.is_featured is not None: listing.is_featured = payload.is_featured
    if payload.ai_risk_score is not None: listing.ai_risk_score = payload.ai_risk_score
    if payload.ai_reject_reason is not None: listing.ai_reject_reason = payload.ai_reject_reason

    db.commit()
    return {"status": "updated", "listing_id": listing.id}

@app.patch("/api/listings/{listing_id}/status")
def update_listing_status(
    listing_id: int,
    payload: ListingStatusUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")

    valid_statuses = ["APPROVED", "REJECTED", "UNDER_REVIEW", "PENDING"]
    if payload.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Noto'g'ri status ko'rsatildi")

    listing.status = payload.status
    if payload.status == "APPROVED":
        if listing.owner:
            listing.owner.trust_score = min(100, listing.owner.trust_score + 5)
    elif payload.status == "REJECTED":
        if listing.owner:
            listing.owner.trust_score = max(0, listing.owner.trust_score - 10)

    db.commit()
    db.refresh(listing)
    return {"status": "success", "new_status": listing.status, "listing_id": listing.id}

@app.patch("/api/listings/{listing_id}/featured")
def toggle_listing_featured(
    listing_id: int,
    payload: ListingFeaturedUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")

    listing.is_featured = payload.is_featured
    db.commit()
    return {"status": "success", "is_featured": listing.is_featured}

@app.delete("/api/listings/{listing_id}")
def delete_listing(
    listing_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")
    db.delete(listing)
    db.commit()
    return {"status": "deleted", "listing_id": listing_id}

# 🚀 Railway API v1 Compatibility Routes
@app.get("/api/v1/listings")
def get_listings_v1(
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return get_listings(status_filter=status_filter, search=search, db=db, admin=None)

@app.post("/api/v1/admin/listings/{listing_id}/unblock")
def unblock_listing_v1(
    listing_id: int,
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")

    listing.status = "APPROVED"
    listing.ai_risk_score = 0
    if listing.owner:
        listing.owner.trust_score = min(100, listing.owner.trust_score + 10)

    db.commit()
    db.refresh(listing)
    return {
        "status": "success",
        "message": "E'lon muvaffaqiyatli unblock qilindi va tasdiqlandi",
        "new_status": "APPROVED",
        "listing_id": listing.id
    }

@app.post("/api/v1/admin/listings/{listing_id}/reject")
def reject_listing_v1(
    listing_id: int,
    db: Session = Depends(get_db)
):
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="E'lon topilmadi")

    listing.status = "REJECTED"
    if listing.owner:
        listing.owner.trust_score = max(0, listing.owner.trust_score - 15)

    db.commit()
    db.refresh(listing)
    return {
        "status": "success",
        "message": "E'lon rad etildi va bloklandi",
        "new_status": "REJECTED",
        "listing_id": listing.id
    }

# 👥 Users Directory Endpoints
@app.get("/api/users")
def get_users(
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    query = db.query(User)
    
    if role and role != "ALL":
        query = query.filter(User.role == role)
    
    if search:
        pattern = f"%{search}%"
        query = query.filter((User.full_name.ilike(pattern)) | (User.phone.ilike(pattern)))

    users = query.order_by(User.created_at.desc()).all()
    
    result = []
    for u in users:
        listings_count = db.query(Listing).filter(Listing.owner_id == u.id).count()
        result.append({
            "id": u.id,
            "full_name": u.full_name,
            "phone": u.phone,
            "role": u.role,
            "trust_score": u.trust_score,
            "status": u.status,
            "listings_count": listings_count,
            "created_at": u.created_at.isoformat() if u.created_at else None
        })
    return result

@app.post("/api/users")
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    existing = db.query(User).filter(User.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ushbu telefon raqamli foydalanuvchi allaqachon mavjud!")

    new_user = User(
        full_name=payload.full_name,
        phone=payload.phone,
        role=payload.role,
        trust_score=payload.trust_score,
        status=payload.status
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "created", "user_id": new_user.id}

@app.put("/api/users/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    if payload.full_name is not None: user.full_name = payload.full_name
    if payload.phone is not None: user.phone = payload.phone
    if payload.role is not None: user.role = payload.role
    if payload.trust_score is not None: user.trust_score = payload.trust_score
    if payload.status is not None: user.status = payload.status

    db.commit()
    return {"status": "updated", "user_id": user.id}

@app.delete("/api/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    db.delete(user)
    db.commit()
    return {"status": "deleted", "user_id": user_id}

@app.patch("/api/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    if payload.status not in ["ACTIVE", "SUSPENDED"]:
        raise HTTPException(status_code=400, detail="Noto'g'ri foydalanuvchi holati")

    user.status = payload.status
    db.commit()
    return {"status": "success", "new_status": user.status, "user_id": user.id}

@app.patch("/api/users/{user_id}/trust-score")
def update_user_trust_score(
    user_id: int,
    payload: UserTrustScoreUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    user.trust_score = max(0, min(100, user.trust_score + payload.delta))
    db.commit()
    return {"status": "success", "new_trust_score": user.trust_score, "user_id": user.id}
