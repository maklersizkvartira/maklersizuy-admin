from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    status: str
    token: str
    username: str
    full_name: str


class UserCreate(BaseModel):
    full_name: str
    phone: str
    password: Optional[str] = "123456"
    role: str = "OWNER" # OWNER or STUDENT
    trust_score: int = 85
    status: str = "ACTIVE"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    trust_score: Optional[int] = None
    status: Optional[str] = None

class UserBase(BaseModel):
    id: int
    full_name: str
    phone: str
    password: Optional[str] = "123456"
    role: str
    trust_score: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class ListingCreate(BaseModel):
    title: str
    description: str
    price: float
    price_period: str = "oylik"
    region: str = "Toshkent sh."
    district: str = "Chilonzor t."
    category: str = "Kvartira"
    room_count: int = 2
    images: Optional[List[str]] = []
    owner_id: int
    status: str = "APPROVED"
    is_featured: bool = False
    ai_risk_score: int = 0
    ai_reject_reason: Optional[str] = None

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    price_period: Optional[str] = None
    region: Optional[str] = None
    district: Optional[str] = None
    category: Optional[str] = None
    room_count: Optional[int] = None
    images: Optional[List[str]] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    ai_risk_score: Optional[int] = None
    ai_reject_reason: Optional[str] = None

class ListingBase(BaseModel):
    id: int
    title: str
    description: str
    price: float
    price_period: str
    region: str
    district: str
    category: str
    room_count: int
    images: str
    owner_id: int
    status: str
    is_featured: bool
    ai_risk_score: int
    ai_reject_reason: Optional[str] = None
    created_at: datetime
    owner: UserBase

    class Config:
        from_attributes = True

class ListingStatusUpdate(BaseModel):
    status: str # APPROVED, REJECTED, UNDER_REVIEW

class ListingFeaturedUpdate(BaseModel):
    is_featured: bool

class UserStatusUpdate(BaseModel):
    status: str # ACTIVE, SUSPENDED

class UserTrustScoreUpdate(BaseModel):
    delta: int # e.g. +5, -10

class DashboardStatsResponse(BaseModel):
    daily_visitors: int
    total_owners: int
    active_owners: int
    total_students: int
    active_students: int
    total_listings: int
    approved_listings: int
    blocked_listings: int
    under_review_listings: int
    ai_auto_approved: int
    ai_rejected_count: int
    admin_unblocked_count: int
    traffic_history: List[dict]
