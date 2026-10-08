"""Tests for initial SQLAlchemy database models (Farmer and Location)."""

import uuid

from sqlalchemy.orm import Session

from backend.app.models.farmer import Farmer
from backend.app.models.location import Location


def test_location_creation_and_hierarchy(db_session: Session) -> None:
    """Test Location creation with District -> Taluk hierarchy and bilingual names."""
    # Create District
    district = Location(
        name_en="Ranipet",
        name_ta="ராணிப்பேட்டை",
        level="district",
        latitude=12.9229,
        longitude=79.3329,
    )
    db_session.add(district)
    db_session.commit()
    db_session.refresh(district)

    assert district.id is not None
    assert isinstance(district.id, uuid.UUID)
    assert district.name_en == "Ranipet"
    assert district.name_ta == "ராணிப்பேட்டை"

    # Create Taluk under District
    taluk = Location(
        name_en="Arakkonam",
        name_ta="அரக்கோணம்",
        level="taluk",
        parent_id=district.id,
        latitude=13.0788,
        longitude=79.6678,
    )
    db_session.add(taluk)
    db_session.commit()
    db_session.refresh(taluk)

    assert taluk.parent_id == district.id
    assert taluk.parent is not None
    assert taluk.parent.name_en == "Ranipet"


def test_farmer_model_preferences_and_consent(db_session: Session) -> None:
    """Test Farmer profile creation with language, theme, and DPDP Act consent."""
    farmer = Farmer(
        name="Murugan",
        phone_hash="hash_dummy_murugan_001",
        language="ta",
        theme_preference="dark",
        district="Ranipet",
        taluk="Arakkonam",
        village="Thakkolam",
        is_consent_given=True,
    )
    db_session.add(farmer)
    db_session.commit()
    db_session.refresh(farmer)

    assert farmer.id is not None
    assert isinstance(farmer.id, uuid.UUID)
    assert farmer.language == "ta"
    assert farmer.theme_preference == "dark"
    assert farmer.is_consent_given is True
    assert farmer.is_active is True
    assert farmer.is_deleted is False
    assert farmer.created_at is not None
