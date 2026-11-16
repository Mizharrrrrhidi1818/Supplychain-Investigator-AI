# n8n Workflow Demonstration — 75–90 Second Video Plan

**Purpose:** Show real evidence of automation and AI tool calling; do not present the video as a production deployment. Record only synthetic order data.

## Recording setup

1. Open your local n8n workflow on Windows and ensure FastAPI is running locally. The existing n8n HTTP Request URL uses `http://host.docker.internal:8000/agent/investigate`.
2. Hide or crop browser tabs, personal accounts, IP addresses, credentials, HTTP authorization headers and tokens. Do not show `.env`.
3. Increase browser zoom until all five nodes are readable. Record at 1080p (1920×1080) if available using OBS Studio, Windows Snipping Tool screen recording, or another tool you already have.
4. Before recording, test the agent once; it sometimes returns truncated narratives. If the model truncates, show that limitation rather than claiming a complete report.

## Storyboard

| Time | What to show | Suggested narration or caption |
|---|---|---|
| 0–10 s | Project title + n8n workflow canvas | “Supplychain-ai investigates purchase-order discrepancies using n8n, FastAPI, and LangChain.” |
| 10–25 s | Webhook + HTTP Request nodes | “A webhook sends an order ID to the Python API.” |
| 25–40 s | Submit synthetic `PO-104` request via PowerShell or Swagger | “The system compares ordered, received, and invoiced quantities.” |
| 40–55 s | Green n8n execution; IF True → Return Exception Report | “The rules detect a 50-unit shortfall and route the case for review.” |
| 55–75 s | API JSON result showing `tools_executed` and `policy_sources` | “The agent called the database and policy-search tools and retrieved three policy sources.” |
| 75–90 s | Docker healthy status on VPS (hide host details) + closing slide | “The backend was containerized on Ubuntu. The model output still needs completeness checks.” |

## Screen capture command for the demo

```powershell
$body = @{ purchase_order_id = "PO-104" } | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:5678/webhook-test/supplychain-investigate" -Method POST -ContentType "application/json" -Body $body
$result | Select-Object purchase_order_id,status,financial_exposure,tools_executed,policy_sources,agent_completed | Format-List
```

Start **Listen for test event** in the n8n Webhook before executing the command. A new listen session may be needed for each test.

## After recording

Save as `docs/videos/supplychain-ai-n8n-demo.mp4` if you intend to commit a small video, or upload to YouTube/LinkedIn and link it from the README. Keep the video short; GitHub repository history grows with large binaries. Do not add a demo-video badge/link until an actual video exists.

Suggested README addition after uploading:

```markdown
### Watch the n8n demo
[Watch the workflow demonstration](PASTE_ACTUAL_VIDEO_URL_HERE)
```
