import os
from datetime import datetime
from agent.reporter.templates import (
    generate_report_header,
    generate_cluster_section,
    generate_report_footer,
)

REPORTS_DIR = "outputs/reports"


def generate_report(analysis: dict) -> str:
    """Generate a full autopsy report from analysis results."""
    print("📝 Reporter Agent: generating autopsy report...\n")

    # Build report
    report = generate_report_header(analysis)

    if analysis["total_failures"] == 0:
        report += "\n## ✅ No Failures Detected\n\nYour LLM app is performing perfectly!\n"
    else:
        for rank, cluster in enumerate(analysis["clusters"], 1):
            report += generate_cluster_section(cluster, rank)

    report += generate_report_footer(analysis)

    # Save report to file
    os.makedirs(REPORTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{REPORTS_DIR}/autopsy_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"✅ Reporter Agent complete!")
    print(f"   - Report saved to: {filename}\n")

    return report


if __name__ == "__main__":
    from agent.fetcher.fetcher_agent import fetch_and_filter_traces
    from agent.analyzer.analyzer_agent import analyze_failures

    results = fetch_and_filter_traces()
    analysis = analyze_failures(results)
    report = generate_report(analysis)
    print(report)