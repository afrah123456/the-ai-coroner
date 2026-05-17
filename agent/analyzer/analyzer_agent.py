from collections import defaultdict
from agent.analyzer.patterns import classify_failure


def analyze_failures(fetcher_results: dict) -> dict:
    """
    Takes fetcher results and clusters failures by pattern,
    then diagnoses root causes.
    """
    print("🧠 Analyzer Agent: clustering failure patterns...\n")

    failed = fetcher_results.get("failed", [])
    successful = fetcher_results.get("successful", [])

    if not failed:
        print("✅ No failures detected!")
        return {
            "total_interactions": len(successful),
            "total_failures": 0,
            "failure_rate": 0.0,
            "clusters": [],
        }

    # Cluster failures by pattern
    clusters = defaultdict(lambda: {
        "pattern": None,
        "count": 0,
        "examples": [],
        "fix": "",
    })

    for trace in failed:
        pattern = classify_failure(trace["output"])
        pattern_name = pattern["name"]

        clusters[pattern_name]["pattern"] = pattern
        clusters[pattern_name]["count"] += 1
        clusters[pattern_name]["fix"] = pattern["fix"]

        # Store up to 2 examples per cluster
        if len(clusters[pattern_name]["examples"]) < 2:
            clusters[pattern_name]["examples"].append({
                "input": trace["input"],
                "output": trace["output"][:150],
            })

    # Sort clusters by count descending
    sorted_clusters = sorted(
        clusters.values(),
        key=lambda x: x["count"],
        reverse=True
    )

    total = len(failed) + len(successful)
    failure_rate = (len(failed) / total * 100) if total > 0 else 0

    print(f"✅ Analyzer Agent complete:")
    print(f"   - {len(failed)} failures across {len(sorted_clusters)} patterns")
    print(f"   - Failure rate: {failure_rate:.1f}%\n")

    return {
        "total_interactions": total,
        "total_failures": len(failed),
        "failure_rate": round(failure_rate, 1),
        "clusters": sorted_clusters,
    }


if __name__ == "__main__":
    from agent.fetcher.fetcher_agent import fetch_and_filter_traces

    results = fetch_and_filter_traces()
    analysis = analyze_failures(results)

    print("\nClusters found:")
    for cluster in analysis["clusters"]:
        print(f"  - {cluster['pattern']['name']}: {cluster['count']} failures")