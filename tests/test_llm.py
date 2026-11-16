
from fastapi.testclient import TestClient

import app.main as main
from app.database import load_data

client = TestClient(main.app)


def test_ai_explanation(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "test_llm.db")
    )
    load_data()

    # Replace the live LLM call with a test response
    def fake_llm(report):
        return (
            "Summary: Delivery discrepancy detected.\n"
            "Business Impact: Invoice requires review.\n"
            "Recommended Actions: Contact the supplier."
        )

    monkeypatch.setattr(
        main,
        "generate_explanation",
        fake_llm
    )

    response = client.post(
        "/explain",
        json={"purchase_order_id": "PO-104"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "EXCEPTION"
    assert data["financial_exposure"] == 1000.0
    assert data["ai_generated"] is True
    assert "Contact the supplier" in data["ai_explanation"]


def test_unknown_order_does_not_call_llm(
    tmp_path, monkeypatch
):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "test_missing.db")
    )
    load_data()

    def fake_llm(report):
        raise AssertionError("LLM must not be called")

    monkeypatch.setattr(
        main,
        "generate_explanation",
        fake_llm
    )

    response = client.post(
        "/explain",
        json={"purchase_order_id": "PO-999"}
    )

    assert response.status_code == 404
