from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_nearby_returns_distance_km(client):
    r = client.get("/api/atms/nearby", params={
        "lat": 30.6046, "lng": 32.2759, "radius_km": 10,
        "working_only": True, "needs_deposit": False,
        "needs_ewallet": False, "needs_currency": False,  # the kwarg that broke things
    })
    assert r.status_code == 200
    data = r.json()
    assert len(data) > 0
    assert all(item["distance_km"] is not None for item in data)
    # And the list should be sorted ascending
    distances = [item["distance_km"] for item in data]
    assert distances == sorted(distances)

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