
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database import load_data

client = TestClient(app)


@pytest.fixture(autouse=True)
def test_database(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "test.db")
    )
    load_data()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_detect_discrepancy():
    response = client.post(
        "/investigate",
        json={"purchase_order_id": "PO-104"}
    )
    assert response.status_code == 200

    result = response.json()
    assert result["status"] == "EXCEPTION"
    assert result["delivery_shortfall"] == 50
    assert result["financial_exposure"] == 1000.0


def test_matching_order():
    response = client.post(
        "/investigate",
        json={"purchase_order_id": "PO-105"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "MATCHED"


def test_unknown_order():
    response = client.post(
        "/investigate",
        json={"purchase_order_id": "PO-999"}
    )
    assert response.status_code == 404
