from agent.fetcher.fetcher_agent import fetch_and_filter_traces
from agent.analyzer.analyzer_agent import analyze_failures
from agent.reporter.reporter_agent import generate_report
from agent.history import save_result
from agent.alerts import send_slack_alert


def run_autopsy(project_name: str = "ai-coroner-demo") -> str:
    print("=" * 60)
    print("THE AI CORONER - Starting Autopsy")
    print("=" * 60 + "\n")

    # Step 1 - Fetch
    fetcher_results = fetch_and_filter_traces(project_name)

    # Step 2 - Analyze
    analysis = analyze_failures(fetcher_results)

    # Step 3 - Report
    report = generate_report(analysis)

    # Step 4 - Save to history
    save_result(analysis, project_name)

    # Step 5 - Send Slack alert with report
    send_slack_alert(analysis, project_name, report)

    print("=" * 60)
    print("Autopsy Complete!")
    print("=" * 60)

    return report


if __name__ == "__main__":
    report = run_autopsy()
    print(report)