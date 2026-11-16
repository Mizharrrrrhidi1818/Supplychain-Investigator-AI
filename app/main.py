
from app.agent import run_agent
from app.rag import get_relevant_policies
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

import httpx

from app.database import find_order
from app.llm import generate_explanation

app = FastAPI(
    title="Supplychain-ai",
    description="AI-ready Supply Chain Exception Investigation API",
    version="0.1.0"
)


class InvestigationRequest(BaseModel):
    purchase_order_id: str = Field(min_length=1)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "project": "Supplychain-ai"
    }


@app.post("/investigate")
def investigate(request: InvestigationRequest):
    order = find_order(request.purchase_order_id)

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Purchase order not found"
        )

    ordered = order["ordered_quantity"]
    received = order["received_quantity"]
    invoiced = order["invoiced_quantity"]

    if received is None or invoiced is None:
        raise HTTPException(
            status_code=409,
            detail="Missing delivery or invoice record"
        )

    delivery_shortfall = max(ordered - received, 0)
    invoice_difference = invoiced - received

    discrepancy = (
        ordered != received or
        invoiced != received
    )

    exposure_cents = max(invoice_difference, 0) * (
        order["unit_price_cents"]
    )

    return {
        "purchase_order_id": order["purchase_order_id"],
        "supplier": order["supplier"],
        "ordered_quantity": ordered,
        "received_quantity": received,
        "invoiced_quantity": invoiced,
        "delivery_shortfall": delivery_shortfall,
        "invoice_difference": invoice_difference,
        "financial_exposure": exposure_cents / 100,
        "currency": "USD",
        "status": "EXCEPTION" if discrepancy else "MATCHED",
        "requires_review": discrepancy
    }


@app.post("/explain")
def explain(request: InvestigationRequest):

    # Step 1: Get the verified investigation report
    report = investigate(request)

    # Step 2: Ask the LLM to explain the report
    try:
        explanation = generate_explanation(report)

    except ValueError as exc:
        print("LLM validation error:", type(exc).__name__)

        raise HTTPException(
            status_code=502,
            detail="LLM configuration or response error"
        ) from exc

    except httpx.TimeoutException as exc:
        print("LLM request timed out")

        raise HTTPException(
            status_code=504,
            detail="LLM request timed out"
        ) from exc

    except httpx.HTTPStatusError as exc:
        status = exc.response.status_code
        print("OpenRouter HTTP status:", status)

        raise HTTPException(
            status_code=503 if status == 429 else 502,
            detail=f"OpenRouter request failed: HTTP {status}"
        ) from exc

    except httpx.RequestError as exc:
        print("LLM connection error:", type(exc).__name__)

        raise HTTPException(
            status_code=502,
            detail="Unable to contact the LLM provider"
        ) from exc

    except (KeyError, IndexError, TypeError) as exc:
        print("Invalid LLM response:", type(exc).__name__)

        raise HTTPException(
            status_code=502,
            detail="Invalid LLM provider response"
        ) from exc

    # Step 3: Return the final report
    result = {
        **report,
        "ai_explanation": explanation,
        "ai_generated": True
    }

    return result


@app.get("/rag/search")
def rag_search(query: str):
    """Retrieve policies without calling an LLM."""

    try:
        policies = get_relevant_policies(query)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    return {
        "query": query,
        "sources": policies,
        "retrieved_count": len(policies)
    }


@app.post("/rag/explain")
def rag_explain(request: InvestigationRequest):
    """Investigate an order using RAG + LLM."""

    # Phase 1: Verified database investigation
    report = investigate(request)

    # Phase 4: Build a retrieval query
    if report["requires_review"]:
        query = (
            "Purchase order delivery shortfall and invoice "
            "quantity mismatch. Receiving verification, "
            "invoice approval, and supplier escalation."
        )
    else:
        query = (
            "Purchase order delivered quantity invoiced "
            "quantity matched. Three-way invoice verification."
        )

    try:
        # Retrieve relevant policies
        policies = get_relevant_policies(query)

        # Include explicit source labels
        policy_context = "\n\n".join(
            f"Source: {item['source']}\n"
            f"{item['content']}"
            for item in policies
        )

        # Generate an explanation grounded in policies
        explanation = generate_explanation(
            report,
            policy_context=policy_context
        )

    except ValueError as exc:
        print(
            "RAG validation error:",
            type(exc).__name__,
            flush=True
        )
        raise HTTPException(
            status_code=502,
            detail="RAG or LLM response validation failed"
        ) from exc

    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="LLM request timed out"
        ) from exc

    except httpx.HTTPStatusError as exc:
        code = exc.response.status_code

        raise HTTPException(
            status_code=503 if code == 429 else 502,
            detail="LLM provider request failed"
        ) from exc

    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=502,
            detail="LLM provider connection failed"
        ) from exc

    return {
        **report,
        "ai_explanation": explanation,
        "ai_generated": True,
        "rag_enabled": True,
        "policy_sources": policies
    }


@app.post("/agent/investigate")
def agent_investigate(request: InvestigationRequest):
    """Run a read-only AI agent investigation."""

    # First validate the order using the trusted
    # deterministic investigation from Phase 1.
    report = investigate(request)

    try:
        agent_result = run_agent(
            request.purchase_order_id
        )

    except ValueError as exc:
        print(
            "Agent validation error:",
            str(exc),
            flush=True
        )
        raise HTTPException(
            status_code=502,
            detail="Agent validation failed"
        ) from exc

    except Exception as exc:
        # Log the traceback locally, not to the API caller.
        import logging
        logging.exception("Agent execution failed")

        raise HTTPException(
            status_code=502,
            detail="AI agent execution failed"
        ) from exc

    return {
        **report,
        **agent_result
    }
