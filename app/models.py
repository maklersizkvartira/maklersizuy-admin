from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

class AdminUser(Base):
    __tablename__ = 'admin_users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, default="Bosh Admin")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, index=True, nullable=False)
    role = Column(String, default="STUDENT")  # OWNER, STUDENT
    trust_score = Column(Integer, default=85) # 0 to 100
    status = Column(String, default="ACTIVE") # ACTIVE, SUSPENDED
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    listings = relationship("Listing", back_populates="owner", cascade="all, delete-orphan")

class Listing(Base):
    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    price_period = Column(String, default="oylik")
    region = Column(String, default="Toshkent sh.")
    district = Column(String, default="Chilonzor t.")
    category = Column(String, default="Kvartira")
    room_count = Column(Integer, default=2)
    images = Column(Text, default="[]")  # JSON string list of image URLs
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Statuses: APPROVED, REJECTED, UNDER_REVIEW, PENDING
    status = Column(String, default="APPROVED", index=True)
    is_featured = Column(Boolean, default=False)
    
    # AI Moderation fields
    ai_risk_score = Column(Integer, default=0) # 0 to 100
    ai_reject_reason = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="listings")

class TrafficMetric(Base):
    __tablename__ = 'traffic_metrics'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, index=True, nullable=False) # YYYY-MM-DD
    daily_visitors = Column(Integer, default=0)
    searches = Column(Integer, default=0)
    new_listings_count = Column(Integer, default=0)
    ai_auto_approved = Column(Integer, default=0)
    ai_flagged = Column(Integer, default=0)

class Report(Base):
    __tablename__ = 'reports'

    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, ForeignKey('listings.id'), nullable=True)
    listing_title = Column(String, nullable=False)
    reporter_name = Column(String, nullable=False)
    reporter_phone = Column(String, nullable=False)
    reason_label = Column(String, nullable=False)
    details = Column(Text, nullable=True)
    status = Column(String, default="PENDING")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
