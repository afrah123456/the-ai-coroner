import json
import os
from datetime import datetime

HISTORY_FILE = "outputs/autopsy_history.json"


def save_result(analysis: dict, project_name: str):
    """Save autopsy result to history file."""
    os.makedirs("outputs", exist_ok=True)

    # Load existing history
    history = load_history()

    # Add new entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "project": project_name,
        "total_interactions": analysis["total_interactions"],
        "total_failures": analysis["total_failures"],
        "failure_rate": analysis["failure_rate"],
        "cluster_count": len(analysis["clusters"]),
        "patterns": [c["pattern"]["name"] for c in analysis["clusters"]]
    }

    history.append(entry)

    # Keep last 100 entries
    history = history[-100:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

    return entry


def load_history(project_name: str = None) -> list:
    """Load autopsy history from file."""
    if not os.path.exists(HISTORY_FILE):
        return []

    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)

        if project_name:
            history = [h for h in history if h["project"] == project_name]

        return history
    except:
        return []