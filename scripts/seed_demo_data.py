"""Seeds synthetic demo farmers, crops, marketplace products, and alerts for local testing.

ALL DATA IS SYNTHETIC AND ARTIFICIAL. NO REAL PII OR REAL CREDENTIALS.
"""

import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.core.security import encrypt_phone, hash_phone
from backend.app.models.alert import RainAlert
from backend.app.models.crop import Crop
from backend.app.models.farmer import Farmer
from backend.app.models.notification import NotificationPreference
from backend.app.models.product import Product

DEMO_FARMERS = [
    {
        "name": "Murugan K (Demo Farmer)",
        "phone": "+919876500001",
        "district": "Ranipet",
        "taluk": "Arakkonam",
        "village": "Thakkolam",
        "lat": 13.0333,
        "lon": 79.7500,
        "language": "ta",
        "theme": "light",
        "crops": [
            {"crop_name": "Paddy (CR 1009)", "crop_type": "grain", "growth_stage": "maturity", "area_acres": 2.5},
            {"crop_name": "Banana (Grand Naine)", "crop_type": "fruit", "growth_stage": "flowering", "area_acres": 1.0},
        ],
        "products": [
            {
                "name_en": "Organic Ponni Paddy (Grade A)",
                "name_ta": "இயற்கை பொன்னி நெல் (தரம் ஏ)",
                "category": "grains",
                "quantity": 25.0,
                "unit": "quintal",
                "price_inr": 2400.0,
                "description": "High yield harvest from Thakkolam, moisture tested and stored in dry bags.",
            }
        ],
    },
    {
        "name": "Selvam R (Demo Farmer)",
        "phone": "+919876500002",
        "district": "Thanjavur",
        "taluk": "Kumbakonam",
        "village": "Dharasuram",
        "lat": 10.9500,
        "lon": 79.3500,
        "language": "ta",
        "theme": "dark",
        "crops": [
            {"crop_name": "Paddy (BPT 5204)", "crop_type": "grain", "growth_stage": "flowering", "area_acres": 3.0},
        ],
        "products": [
            {
                "name_en": "Kumbakonam Country Tomato",
                "name_ta": "கும்பகோணம் நாட்டு தக்காளி",
                "category": "vegetables",
                "quantity": 150.0,
                "unit": "kg",
                "price_inr": 28.0,
                "description": "Freshly picked farm tomatoes, pesticide residue tested.",
            }
        ],
    },
    {
        "name": "Anitha M (Demo Farmer)",
        "phone": "+919876500003",
        "district": "Madurai",
        "lat": 9.9252,
        "lon": 78.1198,
        "language": "en",
        "theme": "light",
        "crops": [
            {
                "crop_name": "Vegetables (Brinjal & Chilli)",
                "crop_type": "vegetables",
                "growth_stage": "vegetative",
                "area_acres": 1.5,
            },
        ],
        "products": [],
    },
]


def seed_demo_data() -> None:
    """Populate database with synthetic farmers, crops, and products."""
    db: Session = SessionLocal()
    try:
        now = datetime.now(UTC)
        for df in DEMO_FARMERS:
            phone_h = hash_phone(df["phone"])
            existing = db.execute(select(Farmer).where(Farmer.phone_hash == phone_h)).scalar_one_or_none()
            if existing:
                continue

            farmer = Farmer(
                name=df["name"],
                phone_hash=phone_h,
                phone_encrypted=encrypt_phone(df["phone"]),
                language=df["language"],
                theme_preference=df["theme"],
                district=df["district"],
                taluk=df.get("taluk"),
                village=df.get("village"),
                latitude=df["lat"],
                longitude=df["lon"],
                is_active=True,
                is_consent_given=True,
                role="farmer",
            )
            db.add(farmer)
            db.flush()

            # Add notification preferences
            pref = NotificationPreference(
                farmer_id=farmer.id,
                channels="whatsapp,sms",
                quiet_hours_enabled=True,
                quiet_start="21:00",
                quiet_end="06:00",
                max_alerts_per_day=3,
            )
            db.add(pref)

            # Add crops
            for c in df["crops"]:
                crop = Crop(
                    farmer_id=farmer.id,
                    crop_name=c["crop_name"],
                    crop_type=c["crop_type"],
                    growth_stage=c["growth_stage"],
                    area_acres=c["area_acres"],
                    sowing_date=now - timedelta(days=45),
                )
                db.add(crop)

            # Add marketplace products
            for p in df["products"]:
                prod = Product(
                    farmer_id=farmer.id,
                    name_en=p["name_en"],
                    name_ta=p["name_ta"],
                    category=p["category"],
                    quantity=p["quantity"],
                    unit=p["unit"],
                    price_inr=p["price_inr"],
                    description=p["description"],
                    district=df["district"],
                    taluk=df.get("taluk", df["district"]),
                    village=df.get("village", df["district"]),
                    harvest_date=now - timedelta(days=2),
                    is_active=True,
                )
                db.add(prod)

            # Add initial demo alert
            alert = RainAlert(
                farmer_id=farmer.id,
                alert_type="24h",
                event_start=now + timedelta(hours=6),
                event_end=now + timedelta(hours=10),
                rainfall_range="20–30 mm",
                probability=85.0,
                severity="HIGH",
                crop_action_en="Check field drainage and protect harvested crops.",
                crop_action_ta="வயல் வடிகால் வசதியை சரிசெய்து அறுவடை பயிர்களை பாதுகாக்கவும்.",
                message_en=f"RAIN ALERT – {df['district'].upper()}\nRain likely between 2 PM and 6 PM. Expected: 20–30 mm. Recommended action: Check field drainage.",
                message_ta=f"மழை எச்சரிக்கை – {df['district']}\nமதியம் 2 முதல் 6 மணி வரை மழை பெய்ய வாய்ப்புள்ளது. எதிர்பார்க்கப்படும் அளவு: 20–30 மி.மீ. வடிகால் வசதியை சரிபார்க்கவும்.",
                idempotency_key=f"{farmer.id}:{now.strftime('%Y%m%d%H')}:24h",
                delivery_status="delivered",
            )
            db.add(alert)

        db.commit()
        print("Successfully seeded synthetic demo farmers, crops, marketplace products, and alerts.")
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
