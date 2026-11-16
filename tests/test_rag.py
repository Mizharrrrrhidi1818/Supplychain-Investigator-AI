
from fastapi.testclient import TestClient

import app.main as main
from app.database import load_data
from app.rag import get_relevant_policies

client = TestClient(main.app)


def test_policy_retrieval():
    results = get_relevant_policies(
        "invoice quantity received quantity approval"
    )

    assert len(results) > 0
    assert all(
        item["source"].endswith(".txt")
        for item in results
    )
    assert all(item["content"] for item in results)


def test_rag_explanation(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "rag_test.db")
    )
    load_data()

    captured = {}

    def fake_llm(report, policy_context=""):
        captured["context"] = policy_context
        return (
            "Summary: Delivery shortfall detected. "
            "Recommended Actions: Review invoice policy."
        )

    monkeypatch.setattr(
        main,
        "generate_explanation",
        fake_llm
    )

    response = client.post(
        "/rag/explain",
        json={"purchase_order_id": "PO-104"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "EXCEPTION"
    assert data["financial_exposure"] == 1000.0
    assert data["rag_enabled"] is True
    assert len(data["policy_sources"]) > 0
    assert "Source:" in captured["context"]
    assert "Review invoice policy" in data["ai_explanation"]


def test_unknown_order_skips_rag(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "missing_order.db")
    )
    load_data()

    def fake_retrieval(query):
        raise AssertionError("RAG should not run")

    monkeypatch.setattr(
        main,
        "get_relevant_policies",
        fake_retrieval
    )

    response = client.post(
        "/rag/explain",
        json={"purchase_order_id": "PO-999"}
    )

    assert response.status_code == 404
