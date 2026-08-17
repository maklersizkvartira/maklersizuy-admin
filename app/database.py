import json
import random
import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, AdminUser, User, Listing, TrafficMetric

SQLALCHEMY_DATABASE_URL = "sqlite:///./maklersiz_admin.db"

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
        # Check if seed is needed
        if db.query(AdminUser).first():
            return

        print("Seeding Maklersiz.uz Admin database with realistic demo data...")

        # 1. Admin account
        admin = AdminUser(
            username="admin",
            password_hash=hash_password("admin123"),
            full_name="Bosh Admin (Maklersiz.uz)"
        )
        db.add(admin)
        db.commit()

        # 2. Users (Home Owners and Students)
        owners_data = [
            ("Azizbek Raximov", "+998901234567", "OWNER", 95, "ACTIVE"),
            ("Dilnoza Karimova", "+998935551234", "OWNER", 88, "ACTIVE"),
            ("Jahongir Qodirov", "+998974008899", "OWNER", 70, "ACTIVE"),
            ("Sardor Umarov", "+998998887766", "OWNER", 45, "SUSPENDED"), # Suspended broker attempt
            ("Malika Shodieva", "+998912223344", "OWNER", 92, "ACTIVE"),
            ("Bobur Alimov", "+998946665544", "OWNER", 30, "SUSPENDED"),
            ("Nigora Tursunova", "+998951112233", "OWNER", 85, "ACTIVE"),
        ]

        students_data = [
            ("Shoxrux Abdullayev", "+998909991122", "STUDENT", 90, "ACTIVE"),
            ("Jasur Mirzayev", "+998931110099", "STUDENT", 85, "ACTIVE"),
            ("Madina Yusupova", "+998977776655", "STUDENT", 95, "ACTIVE"),
            ("Bekzod G'ofurov", "+998943332211", "STUDENT", 80, "ACTIVE"),
            ("Kamola Xasanova", "+998915554433", "STUDENT", 92, "ACTIVE"),
            ("Otabek Ismoilov", "+998994443322", "STUDENT", 88, "ACTIVE"),
        ]

        users = []
        for name, phone, role, trust, status in owners_data + students_data:
            u = User(full_name=name, phone=phone, role=role, trust_score=trust, status=status)
            db.add(u)
            users.append(u)
        
        db.commit()
        for u in users:
            db.refresh(u)

        owners = [u for u in users if u.role == "OWNER"]

        # Realistic Image URLs (Unsplash interior/apartment pics)
        apt_images = [
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?w=800&auto=format&fit=crop&q=60",
            "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800&auto=format&fit=crop&q=60"
        ]

        # 3. AI Blocked / Rejected / Under Review Listings (Crucial Feature 1)
        ai_blocked_listings = [
            {
                "title": "Chilonzor 7-havze 2 xonali kvartira (Talabalar uchun)",
                "description": "Talaba yigit va qizlar uchun qulay sharoitli kvartira. Diqqat: Maklerlik xizmati 15% to'lanadi, shartnoma bilan.",
                "price": 350.0,
                "district": "Chilonzor t.",
                "category": "Kvartira",
                "room_count": 2,
                "owner_id": owners[3].id, # Sardor Umarov (Suspended)
                "status": "REJECTED",
                "ai_risk_score": 92,
                "ai_reject_reason": "🚨 AI Xabardorligi: Matnda 'Maklerlik xizmati 15%' iborasi aniqlandi. Rieltorlik faoliyati belgilari topilgani sababli e'lon rad etildi.",
                "images": json.dumps([apt_images[0], apt_images[1]])
            },
            {
                "title": "Yunusobod 11-kvartal 3 xonali shinam xonadon",
                "description": "Remonti a'lo, barcha maishiy texnika bor. Faqat fotiha qilingan oila yoki 3 ta talaba qizga beriladi. Bog'lanish noutbuk orqali telegramda.",
                "price": 450.0,
                "district": "Yunusobod t.",
                "category": "Kvartira",
                "room_count": 3,
                "owner_id": owners[5].id, # Bobur Alimov
                "status": "REJECTED",
                "ai_risk_score": 85,
                "ai_reject_reason": "⚠️ AI Dublikat Aniqlovi: Ushbu e'lon rasmlari boshqa maklerlik e'lonlarida 3 marta ishlatilgan. Soxta e'lon xavfi yuqori.",
                "images": json.dumps([apt_images[2], apt_images[3]])
            },
            {
                "title": "Tinchlik metrosi yaqinida 1 xonali studiya",
                "description": "Metroga 5 minutlik yo'l. Narxi kelishiladi, depozit bor. Tel: +998901234567 o'rniga boshqa nomer berilgan.",
                "price": 280.0,
                "district": "Shayxontohur t.",
                "category": "Kvartira",
                "room_count": 1,
                "owner_id": owners[2].id,
                "status": "UNDER_REVIEW",
                "ai_risk_score": 68,
                "ai_reject_reason": "🔍 AI Tekshiruvi: Telefon raqam e'londagi profilingiz bilan mos kelmadi va o'rtacha bozordan 40% arzon narx ko'rsatilgan.",
                "images": json.dumps([apt_images[4]])
            },
            {
                "title": "Mirzo Ulug'bek metrosi yonida 2 xona sharoiti bor",
                "description": "Universitet talabalariga ijaraga beriladi. 1 oy oldindan to'lov + 50$ maklersiz emaslik kafolati.",
                "price": 320.0,
                "district": "Mirzo Ulug'bek t.",
                "category": "Kvartira",
                "room_count": 2,
                "owner_id": owners[1].id,
                "status": "UNDER_REVIEW",
                "ai_risk_score": 62,
                "ai_reject_reason": "⚠️ AI Shubha: Matnda tushunarsiz qo'shimcha to'lov shartlari ko'rsatilgan, Admin ko'rib chiqishi shart.",
                "images": json.dumps([apt_images[1], apt_images[3]])
            }
        ]

        # Approved / Active Listings
        approved_listings = [
            {
                "title": "Chilonzor 19-kvartal 2 xonali toza kvartira (Egasidan)",
                "description": "Uy o'zimnikim, maklerlar bezovta qilmasin! Barcha sharoitlar bor: muzlatgich, kir yuvish mashinasi, Wi-Fi. Universitet talabalari uchun mos.",
                "price": 300.0,
                "district": "Chilonzor t.",
                "category": "Kvartira",
                "room_count": 2,
                "owner_id": owners[0].id, # Azizbek Raximov
                "status": "APPROVED",
                "is_featured": True,
                "ai_risk_score": 5,
                "ai_reject_reason": None,
                "images": json.dumps([apt_images[0], apt_images[2]])
            },
            {
                "title": "Yunusobod 4-kvartal 1 xonali shinam xonadon",
                "description": "Uy egasidan to'g'ridan-to mebel va maishiy texnikasi bilan. Metro Yunusobodga 10 minut. Narxi oylik 260$.",
                "price": 260.0,
                "district": "Yunusobod t.",
                "category": "Kvartira",
                "room_count": 1,
                "owner_id": owners[1].id,
                "status": "APPROVED",
                "is_featured": True,
                "ai_risk_score": 8,
                "ai_reject_reason": None,
                "images": json.dumps([apt_images[1], apt_images[4]])
            },
            {
                "title": "Tashkent City yonida premium 3 xonali hovli xonasi",
                "description": "Aralash talabalar va yosh oilalarga mo'ljallangan hovli uyi. Maklersiz to'g'ridan-to'g'ri shartnoma tuziladi.",
                "price": 400.0,
                "district": "Shayxontohur t.",
                "category": "Hovli",
                "room_count": 3,
                "owner_id": owners[4].id,
                "status": "APPROVED",
                "is_featured": False,
                "ai_risk_score": 12,
                "ai_reject_reason": None,
                "images": json.dumps([apt_images[3], apt_images[0]])
            },
            {
                "title": "Olmazor tumani TDTU yonida 2 xonali xonadon",
                "description": "Politexnika universiteti talabalari uchun judayam qulay joylashuv. Gaz, suv, svet uzluksiz. Egasidan.",
                "price": 310.0,
                "district": "Olmazor t.",
                "category": "Kvartira",
                "room_count": 2,
                "owner_id": owners[6].id,
                "status": "APPROVED",
                "is_featured": False,
                "ai_risk_score": 3,
                "ai_reject_reason": None,
                "images": json.dumps([apt_images[2], apt_images[4]])
            }
        ]

        for item in ai_blocked_listings + approved_listings:
            l = Listing(
                title=item["title"],
                description=item["description"],
                price=item["price"],
                district=item["district"],
                category=item["category"],
                room_count=item["room_count"],
                owner_id=item["owner_id"],
                status=item["status"],
                is_featured=item.get("is_featured", False),
                ai_risk_score=item["ai_risk_score"],
                ai_reject_reason=item.get("ai_reject_reason"),
                images=item["images"]
            )
            db.add(l)

        # 4. Traffic Metrics for the last 14 days
        today = datetime.now()
        for i in range(14, -1, -1):
            date_str = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            base_visitors = random.randint(1200, 2800)
            metric = TrafficMetric(
                date=date_str,
                daily_visitors=base_visitors,
                total_searches=base_visitors * random.randint(3, 6),
                new_listings_count=random.randint(15, 45),
                ai_auto_approved=random.randint(12, 38),
                ai_flagged=random.randint(2, 9)
            )
            db.add(metric)

        db.commit()
        print("Database successfully seeded!")
    except Exception as e:
        db.rollback()
        print("Seeding error:", e)
    finally:
        db.close()
