import httpx
import json
from typing import Optional

PHOENIX_BASE_URL = "http://localhost:6006"


def get_traces(project_name: str = "ai-coroner-demo", limit: int = 50) -> list[dict]:
    """Fetch traces from Phoenix via REST API."""

    try:
        response = httpx.get(
            f"{PHOENIX_BASE_URL}/v1/projects/{project_name}/spans",
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        spans = data.get("data", [])
        print(f"✅ Fetched {len(spans)} spans from Phoenix")
        return spans

    except Exception as e:
        print(f"❌ Failed to fetch traces: {e}")
        return []


def get_span_details(span_id: str) -> Optional[dict]:
    """Fetch details of a specific span."""
    url = f"{PHOENIX_BASE_URL}/v1/spans/{span_id}"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"❌ Failed to fetch span {span_id}: {e}")
        return None


if __name__ == "__main__":
    spans = get_traces()
    if spans:
        print("\nFirst span sample:")
        print(json.dumps(spans[0], indent=2))