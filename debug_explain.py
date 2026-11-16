
import traceback

from app.main import investigate, InvestigationRequest
from app.llm import generate_explanation

try:
    report = investigate(
        InvestigationRequest(purchase_order_id="PO-104")
    )

    print("Step 1: Investigation successful")
    print("Status:", report["status"])

    explanation = generate_explanation(report)

    print("Step 2: LLM explanation successful")
    print(explanation)

except Exception as error:
    print("\nERROR TYPE:", type(error).__name__)
    print("ERROR MESSAGE:", str(error))
    print("\nTRACEBACK:")
    traceback.print_exc()
