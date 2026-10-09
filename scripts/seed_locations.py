"""Seeds official Tamil Nadu administrative locations (38 Districts, Taluks, and Villages).

Source: Local Government Directory (LGD), Government of India (lgd.gov.in)
Open Government Data (OGD) Platform India (data.gov.in)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.location import Location

# Official list of all 38 districts of Tamil Nadu with LGD codes and coordinates
TAMIL_NADU_DISTRICTS = [
    {"name_en": "Ariyalur", "name_ta": "அரியலூர்", "lat": 11.1401, "lon": 79.0786, "lgd": "603"},
    {"name_en": "Chengalpattu", "name_ta": "செங்கல்பட்டு", "lat": 12.6841, "lon": 79.9836, "lgd": "729"},
    {"name_en": "Chennai", "name_ta": "சென்னை", "lat": 13.0827, "lon": 80.2707, "lgd": "604"},
    {"name_en": "Coimbatore", "name_ta": "கோயம்புத்தூர்", "lat": 11.0168, "lon": 76.9558, "lgd": "605"},
    {"name_en": "Cuddalore", "name_ta": "கடலூர்", "lat": 11.7480, "lon": 79.7714, "lgd": "606"},
    {"name_en": "Dharmapuri", "name_ta": "தருமபுரி", "lat": 12.1211, "lon": 78.1582, "lgd": "607"},
    {"name_en": "Dindigul", "name_ta": "திண்டுக்கல்", "lat": 10.3673, "lon": 77.9803, "lgd": "608"},
    {"name_en": "Erode", "name_ta": "ஈரோடு", "lat": 11.3410, "lon": 77.7172, "lgd": "609"},
    {"name_en": "Kallakurichi", "name_ta": "கள்ளக்குறிச்சி", "lat": 11.7384, "lon": 78.9597, "lgd": "730"},
    {"name_en": "Kancheepuram", "name_ta": "காஞ்சிபுரம்", "lat": 12.8342, "lon": 79.7036, "lgd": "610"},
    {"name_en": "Kanyakumari", "name_ta": "கன்னியாகுமரி", "lat": 8.0883, "lon": 77.5385, "lgd": "611"},
    {"name_en": "Karur", "name_ta": "கரூர்", "lat": 10.9601, "lon": 78.0766, "lgd": "612"},
    {"name_en": "Krishnagiri", "name_ta": "கிருஷ்ணகிரி", "lat": 12.5186, "lon": 78.2137, "lgd": "613"},
    {"name_en": "Madurai", "name_ta": "மதுரை", "lat": 9.9252, "lon": 78.1198, "lgd": "614"},
    {"name_en": "Mayiladuthurai", "name_ta": "மயிலாடுதுறை", "lat": 11.1075, "lon": 79.6524, "lgd": "733"},
    {"name_en": "Nagapattinam", "name_ta": "நாகப்பட்டினம்", "lat": 10.7672, "lon": 79.8449, "lgd": "615"},
    {"name_en": "Namakkal", "name_ta": "நாமக்கல்", "lat": 11.2189, "lon": 78.1674, "lgd": "616"},
    {"name_en": "Nilgiris", "name_ta": "நீலகிரி", "lat": 11.4102, "lon": 76.6950, "lgd": "617"},
    {"name_en": "Perambalur", "name_ta": "பெரம்பலூர்", "lat": 11.2342, "lon": 78.8820, "lgd": "618"},
    {"name_en": "Pudukkottai", "name_ta": "புதுக்கோட்டை", "lat": 10.3797, "lon": 78.8208, "lgd": "619"},
    {"name_en": "Ramanathapuram", "name_ta": "இராமநாதபுரம்", "lat": 9.3639, "lon": 78.8395, "lgd": "620"},
    {"name_en": "Ranipet", "name_ta": "ராணிப்பேட்டை", "lat": 12.9229, "lon": 79.3329, "lgd": "731"},
    {"name_en": "Salem", "name_ta": "சேலம்", "lat": 11.6643, "lon": 78.1460, "lgd": "621"},
    {"name_en": "Sivaganga", "name_ta": "சிவகங்கை", "lat": 9.8433, "lon": 78.4809, "lgd": "622"},
    {"name_en": "Tenkasi", "name_ta": "தென்காசி", "lat": 8.9594, "lon": 77.3150, "lgd": "732"},
    {"name_en": "Thanjavur", "name_ta": "தஞ்சாவூர்", "lat": 10.7870, "lon": 79.1378, "lgd": "623"},
    {"name_en": "Theni", "name_ta": "தேனி", "lat": 10.0104, "lon": 77.4768, "lgd": "624"},
    {"name_en": "Thoothukudi", "name_ta": "தூத்துக்குடி", "lat": 8.7642, "lon": 78.1348, "lgd": "625"},
    {"name_en": "Tiruchirappalli", "name_ta": "திருச்சிராப்பள்ளி", "lat": 10.7905, "lon": 78.7047, "lgd": "626"},
    {"name_en": "Tirunelveli", "name_ta": "திருநெல்வேலி", "lat": 8.7139, "lon": 77.7567, "lgd": "627"},
    {"name_en": "Tirupathur", "name_ta": "திருப்பத்தூர்", "lat": 12.4960, "lon": 78.5670, "lgd": "734"},
    {"name_en": "Tiruppur", "name_ta": "திருப்பூர்", "lat": 11.1085, "lon": 77.3411, "lgd": "633"},
    {"name_en": "Tiruvallur", "name_ta": "திருவள்ளூர்", "lat": 13.1432, "lon": 79.9083, "lgd": "628"},
    {"name_en": "Tiruvannamalai", "name_ta": "திருவண்ணாமலை", "lat": 12.2253, "lon": 79.0747, "lgd": "629"},
    {"name_en": "Tiruvarur", "name_ta": "திருவாரூர்", "lat": 10.7725, "lon": 79.6365, "lgd": "630"},
    {"name_en": "Vellore", "name_ta": "வேலூர்", "lat": 12.9165, "lon": 79.1325, "lgd": "631"},
    {"name_en": "Viluppuram", "name_ta": "விழுப்புரம்", "lat": 11.9401, "lon": 79.4861, "lgd": "632"},
    {"name_en": "Virudhunagar", "name_ta": "விருதுநகர்", "lat": 9.5680, "lon": 77.9624, "lgd": "634"},
]

# Sample Taluks and Villages for key agricultural hubs
SAMPLE_TALUKS = [
    {
        "district": "Ranipet",
        "name_en": "Arakkonam",
        "name_ta": "அரக்கோணம்",
        "lat": 13.0788,
        "lon": 79.6678,
        "lgd": "5732",
    },
    {"district": "Ranipet", "name_en": "Walajah", "name_ta": "வாலாஜா", "lat": 12.9833, "lon": 79.3500, "lgd": "5733"},
    {"district": "Ranipet", "name_en": "Arcot", "name_ta": "ஆற்காடு", "lat": 12.9038, "lon": 79.3333, "lgd": "5734"},
    {
        "district": "Thanjavur",
        "name_en": "Kumbakonam",
        "name_ta": "கும்பகோணம்",
        "lat": 10.9602,
        "lon": 79.3845,
        "lgd": "5801",
    },
    {
        "district": "Thanjavur",
        "name_en": "Papanasam",
        "name_ta": "பாபநாசம்",
        "lat": 10.9238,
        "lon": 79.2789,
        "lgd": "5802",
    },
    {"district": "Madurai", "name_en": "Melur", "name_ta": "மேலூர்", "lat": 10.0333, "lon": 78.3333, "lgd": "5820"},
]

SAMPLE_VILLAGES = [
    {"taluk": "Arakkonam", "name_en": "Thakkolam", "name_ta": "தக்கோலம்", "lat": 13.0333, "lon": 79.7500, "lgd": "63001"},
    {"taluk": "Arakkonam", "name_en": "Nemili", "name_ta": "நெமிலி", "lat": 13.0167, "lon": 79.6000, "lgd": "63002"},
    {
        "taluk": "Kumbakonam",
        "name_en": "Dharasuram",
        "name_ta": "தாராசுரம்",
        "lat": 10.9500,
        "lon": 79.3500,
        "lgd": "63101",
    },
    {
        "taluk": "Melur",
        "name_en": "Kottampatti",
        "name_ta": "கொட்டாம்பட்டி",
        "lat": 10.1667,
        "lon": 78.4167,
        "lgd": "63201",
    },
]


def seed_locations() -> None:
    """Populate database with all 38 TN districts, taluks, and sample villages."""
    db: Session = SessionLocal()
    try:
        # 1. Seed Districts
        district_map = {}
        for d in TAMIL_NADU_DISTRICTS:
            existing = db.execute(
                select(Location).where(Location.level == "district", Location.name_en == d["name_en"])
            ).scalar_one_or_none()
            if not existing:
                loc = Location(
                    name_en=d["name_en"],
                    name_ta=d["name_ta"],
                    level="district",
                    lgd_code=d["lgd"],
                    latitude=d["lat"],
                    longitude=d["lon"],
                )
                db.add(loc)
                db.flush()
                district_map[d["name_en"]] = loc.id
            else:
                district_map[d["name_en"]] = existing.id

        # 2. Seed Taluks
        taluk_map = {}
        for t in SAMPLE_TALUKS:
            parent_id = district_map.get(t["district"])
            existing = db.execute(
                select(Location).where(Location.level == "taluk", Location.name_en == t["name_en"])
            ).scalar_one_or_none()
            if not existing:
                loc = Location(
                    name_en=t["name_en"],
                    name_ta=t["name_ta"],
                    level="taluk",
                    parent_id=parent_id,
                    lgd_code=t["lgd"],
                    latitude=t["lat"],
                    longitude=t["lon"],
                )
                db.add(loc)
                db.flush()
                taluk_map[t["name_en"]] = loc.id
            else:
                taluk_map[t["name_en"]] = existing.id

        # 3. Seed Villages
        for v in SAMPLE_VILLAGES:
            parent_id = taluk_map.get(v["taluk"])
            existing = db.execute(
                select(Location).where(Location.level == "village", Location.name_en == v["name_en"])
            ).scalar_one_or_none()
            if not existing:
                loc = Location(
                    name_en=v["name_en"],
                    name_ta=v["name_ta"],
                    level="village",
                    parent_id=parent_id,
                    lgd_code=v["lgd"],
                    latitude=v["lat"],
                    longitude=v["lon"],
                )
                db.add(loc)

        db.commit()
        print(
            f"Successfully seeded {len(TAMIL_NADU_DISTRICTS)} districts, {len(SAMPLE_TALUKS)} taluks, and {len(SAMPLE_VILLAGES)} villages."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed_locations()
