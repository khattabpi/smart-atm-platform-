"""Seed the database with demo ATMs for testing (NYC + Egypt)."""
from app.database import SessionLocal, engine, Base
from app.models.atm import ATM

SAMPLE_ATMS = [
    # ===== Egypt (Cairo / Ismailia / Suez) =====
    {
        "name": "CIB Smart ATM - Nasr City", "bank": "CIB", "address": "Nasr City, Cairo",
        "latitude": 30.0566, "longitude": 31.3290,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD", "EUR"],
        "is_working": True, "rating": 4.7, "reliability_score": 0.95,
    },
    {
        "name": "Banque Misr - Tahrir", "bank": "Banque Misr", "address": "Tahrir Square, Cairo",
        "latitude": 30.0444, "longitude": 31.2357,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": False,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD"],
        "is_working": True, "rating": 4.2, "reliability_score": 0.88,
    },
    {
        "name": "NBE - Heliopolis Branch", "bank": "National Bank of Egypt",
        "address": "Heliopolis, Cairo",
        "latitude": 30.0900, "longitude": 31.3400,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": True,
        "currency_exchange": False, "supported_currencies": ["EGP"],
        "is_working": True, "rating": 4.0, "reliability_score": 0.82,
    },
    {
        "name": "QNB Alahli - New Cairo", "bank": "QNB Alahli", "address": "Fifth Settlement, Cairo",
        "latitude": 30.0288, "longitude": 31.4910,
        "cash_withdrawal": True, "cash_deposit": False, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD", "EUR", "GBP"],
        "is_working": True, "rating": 4.5, "reliability_score": 0.92,
    },
    {
        "name": "HSBC - Maadi", "bank": "HSBC", "address": "Maadi, Cairo",
        "latitude": 29.9602, "longitude": 31.2569,
        "cash_withdrawal": True, "cash_deposit": False, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD", "EUR", "GBP"],
        "is_working": False, "rating": 3.5, "reliability_score": 0.40,
    },
    # Ismailia / Suez area (closer to your detected location 30.6046, 32.2759)
    {
        "name": "CIB - Ismailia Center", "bank": "CIB", "address": "Ismailia",
        "latitude": 30.5965, "longitude": 32.2715,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD", "EUR"],
        "is_working": True, "rating": 4.6, "reliability_score": 0.94,
    },
    {
        "name": "Banque Misr - Ismailia", "bank": "Banque Misr", "address": "Ismailia",
        "latitude": 30.6080, "longitude": 32.2820,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": False,
        "currency_exchange": False, "supported_currencies": ["EGP"],
        "is_working": True, "rating": 4.0, "reliability_score": 0.85,
    },
    {
        "name": "NBE - Ismailia Branch", "bank": "National Bank of Egypt", "address": "Ismailia",
        "latitude": 30.6020, "longitude": 32.2700,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD"],
        "is_working": True, "rating": 4.3, "reliability_score": 0.90,
    },
    {
        "name": "QNB - Suez Canal University", "bank": "QNB Alahli", "address": "Ismailia",
        "latitude": 30.6150, "longitude": 32.2790,
        "cash_withdrawal": True, "cash_deposit": False, "ewallet_support": True,
        "currency_exchange": False, "supported_currencies": ["EGP"],
        "is_working": True, "rating": 4.1, "reliability_score": 0.86,
    },
    {
        "name": "HSBC - Port Said Road", "bank": "HSBC", "address": "Ismailia",
        "latitude": 30.5900, "longitude": 32.2900,
        "cash_withdrawal": True, "cash_deposit": False, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["EGP", "USD", "EUR"],
        "is_working": True, "rating": 4.4, "reliability_score": 0.91,
    },

    # ===== NYC (kept for international demo) =====
    {
        "name": "Wall Street ATM", "bank": "HSBC", "address": "Wall St, NYC",
        "latitude": 40.7074, "longitude": -74.0113,
        "cash_withdrawal": True, "cash_deposit": False, "ewallet_support": True,
        "currency_exchange": True, "supported_currencies": ["USD", "EUR", "CNY", "GBP"],
        "is_working": True, "rating": 4.7, "reliability_score": 0.98,
    },
    {
        "name": "Times Square ATM", "bank": "Citibank", "address": "Broadway, NYC",
        "latitude": 40.7580, "longitude": -73.9855,
        "cash_withdrawal": True, "cash_deposit": True, "ewallet_support": False,
        "currency_exchange": True, "supported_currencies": ["USD", "EUR", "JPY"],
        "is_working": True, "rating": 3.8, "reliability_score": 0.7,
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(ATM).count() > 0:
            print("DB already seeded.")
            return
        for atm in SAMPLE_ATMS:
            db.add(ATM(**atm))
        db.commit()
        print(f"Seeded {len(SAMPLE_ATMS)} ATMs.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()