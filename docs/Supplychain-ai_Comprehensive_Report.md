# Supplychain-ai — Comprehensive Project Report

**AI Engineering × Data Engineering × Cloud Engineering**  
**Project type:** Applied portfolio MVP using synthetic supply-chain data  
**Evidence date:** November 15, 2026  
**Status:** Verified containerized investigation and tool-calling demonstration; unresolved narrative truncation

## Executive summary

Supplychain-ai is a prototype for investigating mismatches between purchase orders, goods receipts, and supplier invoices. It uses Python and SQLite to calculate verified discrepancies; n8n to accept and route requests; LangChain and Chroma to retrieve fictional company policies; OpenRouter to generate explanations; and a LangChain agent to call two read-only tools. A Dockerized FastAPI service was deployed on an Ubuntu VPS and returned HTTP 200 for both deterministic and agent-based investigation calls. The model's final narrative in the observed cloud response ended abruptly, therefore output completeness remains an open reliability issue.

## 1. Motivation and background

Procurement, receiving, and accounts-payable teams often rely on records that do not perfectly match. A quantity difference can affect invoice review, stock visibility, vendor follow-up, and operational planning. Reconciling these records manually is repetitive and can result in inconsistent escalation. Supplychain-ai explores whether a small system can combine deterministic validation with contextual document retrieval, while keeping financial decisions under human control. The domain is realistic, but project inputs and policies are fictional and do not establish real-world business outcomes.

## 2. Objectives

1. Ingest and validate sample purchase-order, delivery, and invoice data in SQLite.
2. Identify quantity mismatches and calculate a provisional invoice exposure using verified values.
3. Expose investigation endpoints with FastAPI, suitable for automated access.
4. Orchestrate the investigation using an n8n webhook, HTTP Request, IF branch, and webhook response.
5. Retrieve applicable policy excerpts using LangChain, Chroma, and local TF-IDF vectors.
6. Demonstrate a LangChain agent selecting and executing a read-only purchase-order tool and policy-search tool.
7. Package the application in Docker and verify health and investigation responses on an Ubuntu VPS.
8. Document methods, tests, constraints, results, and future improvements transparently for a portfolio.

## 3. Fundamental theory

### 3.1 Three-way matching

Three-way matching compares purchase-order quantities, receiving records, and invoice quantities. A mismatch does not necessarily imply fraud, accounting loss, or contract breach; partial shipments or timing differences may explain it. The sample demonstrates `ordered = 500`, `received = 450`, and `invoiced = 500`.

### 3.2 Deterministic data processing

SQL joins and Python rules are used to retrieve and compare related records. The delivery shortfall is `max(ordered − received, 0) = 50 units`; the billed-over-received quantity is `invoiced − received = 50 units`. Given a sample price of $20 per unit, the provisional over-invoiced exposure is `max(invoiced − received, 0) × $20 = $1,000`. This is a screening metric, not a validated financial loss or payment instruction.

### 3.3 REST API and event-driven automation

FastAPI provides HTTP endpoints. n8n receives an event via Webhook, calls the API via HTTP Request, checks the boolean `requires_review`, and returns the result through the corresponding Respond to Webhook node. An exported five-node workflow and a screenshot document the successful exception branch. The locally hosted n8n demonstration should not be confused with deployment of n8n on the VPS.

### 3.4 Language models and prompt grounding

The LLM generates business-readable language based on structured numbers. Numbers should be obtained from verified calculations, not invented in free-form generation. Prompt instructions limit recommendations to human-reviewed actions, but prompting alone cannot guarantee factual correctness or response completeness.

### 3.5 Retrieval-augmented generation

RAG searches a corpus of policy documents and supplies relevant excerpts to the LLM. In this implementation, `langchain-text-splitters` divides the three fictional text policies into chunks, `scikit-learn` TF-IDF encodes chunks as sparse lexical vectors, and Chroma supports similarity retrieval. TF-IDF is a lightweight lexical approach and should not be described as a pretrained semantic embedding model. Source filenames are attached as retrieval evidence.

### 3.6 Agent tool calling

The LangChain agent is given two read-only tools: `get_purchase_order` and `search_company_policies`. Tool outputs return database facts and policy passages, respectively. A successful tool-calling response requires observing both names in the execution trace, not merely accepting a model assertion that tools were used. The agent cannot directly modify payment status or inventory records using these tools.

### 3.7 Containerization and cloud operations

Docker packages application dependencies; Compose configures environment injection, persistent SQLite storage, health checks, port exposure, restarts, and log rotation. The VPS binds port 8000 to `127.0.0.1` and can be reached from the Windows workstation over SSH tunneling. These are deployment fundamentals rather than a complete secure production architecture.

## 4. Research / development methodology

**Method:** Iterative build–test–debug development of a single realistic incident scenario. The MVP was assembled across seven roadmap phases: API and data engineering; n8n; LLM integration; RAG; agents; Docker/VPS; portfolio documentation.

**Inputs:** Two fictional purchase orders, matching delivery/invoice CSVs, and three fictitious policy text files (`receiving_policy.txt`, `invoice_policy.txt`, `supplier_escalation.txt`). No personal customer information or actual supplier contracts were used.

**Pipeline:** CSV → validated SQLite schema → deterministic investigation → policy retrieval → read-only agent tool calls → AI narrative → FastAPI JSON response → n8n exception/matched routing. Hosted OpenRouter was used for inference rather than a local LLM.

**Verification approach:** The user exercised `/investigate` and `/agent/investigate` on the Ubuntu VPS via `curl`, and supplied the n8n execution screenshot and export. Original project tests were designed in earlier phases, but no final complete Pytest output was provided for this report; automated test pass counts should therefore not be presented as independently verified.

## 5. Implementation and system architecture

**Application layer:** FastAPI exposes `/health`, `/investigate`, `/explain`, `/rag/search`, `/rag/explain`, and `/agent/investigate`.

**Structured data layer:** SQLite stores sample orders, receipts and invoices. `app/bootstrap.py` checks for existing records at container startup and avoids re-importing sample data when records already exist. The VPS reported the database at `/app/storage/supplychain.db` on the persistent storage volume.

**RAG layer:** LangChain documents and text splitting feed a cached, in-memory Chroma store built with local TF-IDF vectors. Three policy filenames were present in the observed agent response. Retrieved policies are advisory reference text, not authoritative operational instructions.

**Agent layer:** The model chooses the order investigation and policy retrieval tools; the service returns `tools_executed`, `policy_sources`, the deterministic report and AI explanation.

**Automation layer:** The supplied workflow export contains Webhook → HTTP Request → IF → Respond to Webhook for both branches. The HTTP Request targets `http://host.docker.internal:8000/agent/investigate` in local Docker-on-Windows development. The workflow export is marked inactive; testing used the test webhook path.

**Cloud layer:** Docker Compose starts the FastAPI service with `python -m app.bootstrap` followed by Uvicorn. API access remained bound to the VPS loopback interface. No evidence was provided of publicly accessible n8n or a cloud-hosted video dashboard.

## 6. Results and discussion

### 6.1 Verified quantitative result

In the synthetic PO-104 scenario, the VPS returned HTTP 200 for `/investigate` with ordered quantity 500, received quantity 450, invoiced quantity 500, delivery shortfall 50, invoice difference 50, provisional exposure $1,000 USD, and `requires_review: true`. This confirms working database access and deterministic exception calculation in the container.

### 6.2 Verified agent execution

The VPS returned HTTP 200 for `/agent/investigate` with `tools_executed: [get_purchase_order, search_company_policies]`, all three policy filenames, and `agent_completed: true`. This demonstrates that both read-only tools were executed in the observed request and the service returned their evidence references.

### 6.3 Important limitation — truncated narrative

The agent explanation returned to the user was cut off in the Business Impact section, ending inside the text `verified receipts (45`. Earlier Windows examples also stopped mid-sentence. Thus, the result demonstrates a successful API call and tool execution but **not a complete professional investigation report**. The current `agent_completed` field indicates that the LangChain invocation ended, not that all required headings and sentences were validated. To address this, future work should inspect finish reasons, validate required sections, control output budgets, and return a distinct `report_complete` boolean rather than equating final response with completeness.

### 6.4 Reliability and safety

The free OpenRouter router previously produced intermittent HTTP 502 validation failures. A provider call can succeed with minimal text and still fail on a longer agent request. Tool calling consumes additional model calls and may hit capability limits. Recommendations should remain suggestions for authorized finance, inventory, or procurement staff, never automatic payment holds, stock changes, or supplier sanctions. The API is not publicly authenticated and must remain private in this MVP.

### 6.5 Deployment troubleshooting and lessons

An early VPS `500 Internal Server Error` arose because the SQLite database lacked tables; running the database ingestion initialized the schema. The Dockerfile was then corrected to execute `app.bootstrap` at startup, and the logs confirmed that existing order records were preserved on restart. A subsequent 502 agent error was traced in part to `OPENROUTER_API_KEY` missing from the container; loading it through a protected VPS `.env` and recreating the container allowed the subsequent HTTP 200 agent test. These troubleshooting steps illustrate container lifecycle and environment configuration skills.

## 7. Limitations and next steps

- Synthetic, minimal two-order dataset; no measured performance, accuracy, or business savings.
- Lexical TF-IDF retrieval rather than a pretrained semantic embedding model.
- Agent output truncation and intermittent provider errors; final response-completeness validation is absent.
- No production authentication, authorization, audit-grade monitoring, backup policy, CI/CD, or immutable dependencies.
- n8n demonstrated locally; cloud deployment applies to FastAPI, SQLite and RAG/agent code only.
- No independent evidence of a final complete Pytest run or sustained performance under load.

Recommended next improvements (outside the three-hour MVP): automated completeness checks, capped agent execution and consistent error handling, authenticated API access, more realistic multi-delivery schemas, dataset-level evaluation, infrastructure monitoring, and a proper approval workflow.

## 8. Conclusion

Supplychain-ai successfully demonstrates an end-to-end portfolio architecture spanning deterministic data engineering, n8n automation, LangChain RAG, AI-agent tool calling, and private Docker deployment on an Ubuntu VPS. The observed HTTP 200 responses and executed tools support claims of functional integration. The partial AI narrative and intermittent provider reliability make the current state an experimental MVP, not an autonomous supply-chain decision system. As a portfolio artifact, the project offers concrete evidence of cross-disciplinary development while transparently documenting what has and has not been verified.

## Appendix A — Observed artifacts

- Exported n8n workflow (sanitized): `workflows/supplychain_n8n.json`
- n8n successful exception path screenshot: `docs/images/n8n-workflow-success.png`
- Observed VPS agent response (with truncation note): `examples/po104_vps_result.json`
- GitHub README: `README.md`

## Appendix B — References for underlying technologies

- Python: https://www.python.org/
- FastAPI documentation: https://fastapi.tiangolo.com/
- LangChain documentation: https://docs.langchain.com/
- Chroma documentation: https://docs.trychroma.com/
- n8n documentation: https://docs.n8n.io/
- Docker Compose documentation: https://docs.docker.com/compose/
- OpenRouter API documentation: https://openrouter.ai/docs/
