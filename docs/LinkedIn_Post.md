# LinkedIn post — Supplychain-ai

I wanted to explore a common operations problem: what happens when a supplier invoice says 500 units, but the warehouse has received only 450? I built **Supplychain-ai**, a portfolio project that checks purchase orders, delivery records, and invoices, then flags discrepancies for human review. In my sample case, the system identified a 50-unit shortfall and $1,000 in provisional financial exposure.

The project combines Python, FastAPI, SQLite, n8n, LangChain RAG, and an AI agent with two read-only tools: one for verified purchase-order data and another for company policy retrieval. I also containerized the backend with Docker and tested it on an Ubuntu VPS. Both agent tools executed successfully in the VPS test, and n8n routed the exception through the workflow.

This project taught me how much engineering work sits around an LLM: data integrity, orchestration, environment variables, deployment, and error handling. The generated report still needs more robust completeness validation, so I see this as a functional MVP rather than a finished production system. I’m documenting the architecture, workflow, and lessons learned on GitHub. #AIEngineering #DataEngineering #CloudEngineering #LangChain #n8n #Python #Docker
