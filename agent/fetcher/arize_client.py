import httpx
import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

PHOENIX_BASE_URL = "http://localhost:6006"
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")


def is_phoenix_running() -> bool:
    """Check if local Phoenix is running."""
    try:
        response = httpx.get(f"{PHOENIX_BASE_URL}/v1/projects", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_traces_from_phoenix(project_name: str, limit: int) -> list[dict]:
    """Fetch traces from local Phoenix."""
    try:
        response = httpx.get(
            f"{PHOENIX_BASE_URL}/v1/projects/{project_name}/spans",
            timeout=10
        )
        response.raise_for_status()
        spans = response.json().get("data", [])
        print(f"Fetched {len(spans)} spans from local Phoenix")
        return spans
    except Exception as e:
        print(f"Phoenix fetch failed: {e}")
        return []


def get_traces_from_arize(project_name: str, limit: int) -> list[dict]:
    """Fetch traces from Arize cloud API."""
    try:
        # Use Arize REST API to fetch spans
        headers = {
            "Authorization": f"Bearer {ARIZE_API_KEY}",
            "arize-space-id": ARIZE_SPACE_ID,
        }

        response = httpx.get(
            f"https://api.arize.com/v1/spans",
            headers=headers,
            params={
                "project_name": project_name,
                "limit": limit
            },
            timeout=10
        )

        if response.status_code == 200:
            spans = response.json().get("data", [])
            print(f"Fetched {len(spans)} spans from Arize cloud")
            return spans
        else:
            print(f"Arize API returned {response.status_code}")
            return []

    except Exception as e:
        print(f"Arize cloud fetch failed: {e}")
        return []


def get_traces(project_name: str = "ai-coroner-demo", limit: int = 50) -> list[dict]:
    """
    Fetch traces — tries local Phoenix first, falls back to Arize cloud.
    """
    # Try local Phoenix first
    if is_phoenix_running():
        print("Using local Phoenix...")
        spans = get_traces_from_phoenix(project_name, limit)
        if spans:
            return spans

    # Fall back to Arize cloud
    print("Local Phoenix not available, trying Arize cloud...")
    return get_traces_from_arize(project_name, limit)


def get_span_details(span_id: str) -> Optional[dict]:
    """Fetch details of a specific span."""
    url = f"{PHOENIX_BASE_URL}/v1/spans/{span_id}"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        print(f"Failed to fetch span {span_id}: {e}")
        return None


if __name__ == "__main__":
    spans = get_traces()
    if spans:
        print(f"\nFirst span sample:")
        print(json.dumps(spans[0], indent=2))