
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
model = os.getenv("OPENROUTER_MODEL", "openrouter/free")

if not api_key:
    raise SystemExit("Missing OPENROUTER_API_KEY")

try:
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": "Reply with exactly: CONNECTION OK"
                }
            ],
            "max_tokens": 100
        },
        timeout=60.0
    )

    print("HTTP status:", response.status_code)

    data = response.json()

    if "error" in data:
        error = data["error"]
        print("Provider error code:", error.get("code"))
        print("Provider error message:", error.get("message"))
    elif response.is_success:
        choices = data.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            print("Model:", data.get("model"))
            print("LLM reply:", message.get("content"))
            print(
                "Finish reason:",
                choices[0].get("finish_reason")
            )
        else:
            print("No completion choices returned")
    else:
        print("Request unsuccessful")

except httpx.TimeoutException:
    print("ERROR: OpenRouter request timed out")

except httpx.RequestError as exc:
    print("ERROR: Connection failed:", type(exc).__name__)

except ValueError:
    print("ERROR: OpenRouter returned invalid JSON")
