
from fastapi.testclient import TestClient

import app.main as main
from app.database import load_data
from app.agent import (
    get_purchase_order,
    search_company_policies
)

client = TestClient(main.app)


def test_purchase_order_tool(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "agent_test.db")
    )
    load_data()

    result = get_purchase_order.invoke({
        "purchase_order_id": "PO-104"
    })

    assert '"EXCEPTION"' in result
    assert '"delivery_shortfall": 50' in result


def test_policy_search_tool():
    result = search_company_policies.invoke({
        "query": "invoice quantity mismatch"
    })

    assert "source" in result
    assert "content" in result


def test_agent_endpoint(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "SUPPLYCHAIN_DB_PATH",
        str(tmp_path / "endpoint_test.db")
    )
    load_data()

    # Mock the LLM agent, not the database.
    def fake_agent(purchase_order_id):
        return {
            "purchase_order_id": purchase_order_id,
            "agent_explanation": "Human review required.",
            "tools_executed": [
                "get_purchase_order",
                "search_company_policies"
            ],
            "policy_sources": ["invoice_policy.txt"],
            "agent_completed": True
        }

    monkeypatch.setattr(
        main, "run_agent", fake_agent
    )

    response = client.post(
        "/agent/investigate",
        json={"purchase_order_id": "PO-104"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "EXCEPTION"
    assert data["financial_exposure"] == 1000.0
    assert data["agent_completed"] is True
    assert len(data["tools_executed"]) == 2
