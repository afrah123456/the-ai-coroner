from agent.fetcher.arize_client import get_traces
import json

FAILURE_KEYWORDS = [
    "i'm not able",
    "i cannot",
    "i'm sorry",
    "i don't understand",
    "that's not something",
    "outside my scope",
    "i'm unable",
    "not a valid",
    "doesn't make sense",
    "i appreciate",
    "philosophical",
    "not a tax",
    "unfortunately",
]


def is_potential_failure(output: str) -> bool:
    """Check if a response looks like a failure or poor handling."""
    output_lower = output.lower()
    return any(keyword in output_lower for keyword in FAILURE_KEYWORDS)


def fetch_and_filter_traces(project_name: str = "ai-coroner-demo") -> dict:
    """Fetch all traces from Phoenix and split into successful and failed."""
    print("🔍 Fetcher Agent: pulling traces from Phoenix...\n")

    spans = get_traces(project_name=project_name)

    if not spans:
        print("❌ No spans found.")
        return {"successful": [], "failed": []}

    successful = []
    failed = []

    for span in spans:
        attributes = span.get("attributes", {})

        # Extract user input from attributes
        user_input = attributes.get("llm.input_messages.1.message.content", "")

        # Extract assistant output from attributes
        assistant_output = attributes.get("llm.output_messages.0.message.content", "")

        if not user_input or not assistant_output:
            continue

        trace_data = {
            "span_id": span.get("context", {}).get("span_id", ""),
            "input": user_input,
            "output": assistant_output,
            "latency_ms": span.get("attributes", {}).get("llm.token_count.total", 0),
        }

        if is_potential_failure(assistant_output):
            failed.append(trace_data)
        else:
            successful.append(trace_data)

    print(f"✅ Fetcher Agent complete:")
    print(f"   - {len(successful)} successful interactions")
    print(f"   - {len(failed)} potential failures\n")

    return {"successful": successful, "failed": failed}


if __name__ == "__main__":
    results = fetch_and_filter_traces()
    print("Failed interactions:")
    for f in results["failed"]:
        print(f"  Q: {f['input'][:60]}")
        print(f"  A: {f['output'][:60]}\n")