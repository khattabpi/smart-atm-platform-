from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200


def test_nearby():
    r = client.get("/api/atms/nearby?lat=40.7128&lng=-74.0060&radius_km=10")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_recommendation():
    r = client.post("/api/recommendations/", json={
        "latitude": 40.7128, "longitude": -74.0060,
        "needs_deposit": False
    })
    assert r.status_code == 200
    body = r.json()
    assert "best_atm" in body