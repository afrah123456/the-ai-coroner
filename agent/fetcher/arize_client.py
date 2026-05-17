import httpx
import json
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
PHOENIX_API_KEY = os.getenv("PHOENIX_API_KEY")
PHOENIX_SPACE_URL = os.getenv("PHOENIX_SPACE_URL", "https://app.phoenix.arize.com/s/shahabuddin-af")

LOCAL_PHOENIX_URL = "http://localhost:6006"


def is_phoenix_running() -> bool:
    """Check if local Phoenix is running."""
    try:
        response = httpx.get(f"{LOCAL_PHOENIX_URL}/v1/projects", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_traces(project_name: str = "ai-coroner-demo", limit: int = 50) -> list[dict]:
    """
    Fetch traces — tries local Phoenix first, falls back to Arize cloud Phoenix.
    """
    # Try local Phoenix first
    if is_phoenix_running():
        print("Using local Phoenix...")
        try:
            response = httpx.get(
                f"{LOCAL_PHOENIX_URL}/v1/projects/{project_name}/spans",
                timeout=10
            )
            response.raise_for_status()
            spans = response.json().get("data", [])
            if spans:
                print(f"Fetched {len(spans)} spans from local Phoenix")
                return spans
        except Exception as e:
            print(f"Local Phoenix failed: {e}")

    # Fall back to Arize cloud Phoenix
    print("Using Arize cloud Phoenix...")
    try:
        response = httpx.get(
            f"{PHOENIX_SPACE_URL}/v1/projects/{project_name}/spans",
            headers={
                "Authorization": f"Bearer {PHOENIX_API_KEY}",
            },
            timeout=10
        )
        print(f"Status: {response.status_code}")
        response.raise_for_status()
        spans = response.json().get("data", [])
        print(f"Fetched {len(spans)} spans from Arize cloud Phoenix")
        return spans
    except Exception as e:
        print(f"Arize cloud Phoenix failed: {e}")
        return []


def get_span_details(span_id: str) -> Optional[dict]:
    """Fetch details of a specific span."""
    for base_url, headers in [
        (LOCAL_PHOENIX_URL, {}),
        (PHOENIX_SPACE_URL, {"Authorization": f"Bearer {PHOENIX_API_KEY}"})
    ]:
        try:
            response = httpx.get(
                f"{base_url}/v1/spans/{span_id}",
                headers=headers,
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
        except:
            continue
    return None


if __name__ == "__main__":
    spans = get_traces()
    if spans:
        print(f"\nFirst span sample:")
        print(json.dumps(spans[0], indent=2))
    else:
        print("No spans found")