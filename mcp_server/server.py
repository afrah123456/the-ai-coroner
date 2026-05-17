import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'utf-8'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastmcp import FastMCP
from agent.fetcher.fetcher_agent import fetch_and_filter_traces
from agent.analyzer.analyzer_agent import analyze_failures
from agent.reporter.reporter_agent import generate_report

# Create MCP server
mcp = FastMCP(
    name="The AI Coroner",
    instructions="An autonomous LLM diagnostic agent that fetches traces from Arize Phoenix, detects failure patterns, and generates autopsy reports."
)


@mcp.tool()
def fetch_traces(project_name: str = "ai-coroner-demo") -> dict:
    """Fetch and filter traces from Arize Phoenix for a given project."""
    results = fetch_and_filter_traces(project_name)
    return {
        "successful_count": len(results["successful"]),
        "failed_count": len(results["failed"]),
        "successful": results["successful"][:3],
        "failed": results["failed"][:3],
    }


@mcp.tool()
def analyze_traces(project_name: str = "ai-coroner-demo") -> dict:
    """Fetch traces and analyze failure patterns for a given project."""
    fetcher_results = fetch_and_filter_traces(project_name)
    analysis = analyze_failures(fetcher_results)
    return {
        "total_interactions": analysis["total_interactions"],
        "total_failures": analysis["total_failures"],
        "failure_rate": analysis["failure_rate"],
        "cluster_count": len(analysis["clusters"]),
        "clusters": [
            {
                "pattern": c["pattern"]["name"],
                "count": c["count"],
                "description": c["pattern"]["description"],
                "fix": c["fix"],
            }
            for c in analysis["clusters"]
        ]
    }


@mcp.tool()
def run_full_autopsy(project_name: str = "ai-coroner-demo") -> dict:
    """
    Run the full AI Coroner autopsy pipeline on a project.
    Fetches traces, analyzes failures, and generates a complete report.
    """
    fetcher_results = fetch_and_filter_traces(project_name)
    analysis = analyze_failures(fetcher_results)
    report = generate_report(analysis)

    return {
        "total_interactions": analysis["total_interactions"],
        "total_failures": analysis["total_failures"],
        "failure_rate": analysis["failure_rate"],
        "health": "Healthy" if analysis["failure_rate"] < 20 else
        "Needs Attention" if analysis["failure_rate"] < 50 else
        "Critical",
        "clusters": [
            {
                "pattern": c["pattern"]["name"],
                "count": c["count"],
                "fix": c["fix"],
            }
            for c in analysis["clusters"]
        ],
        "report": report
    }


@mcp.tool()
def list_monitored_projects() -> dict:
    """List all projects being monitored in Arize Phoenix."""
    import httpx
    try:
        response = httpx.get("http://localhost:6006/v1/projects", timeout=5)
        projects = response.json().get("data", [])
        return {
            "projects": [p["name"] for p in projects if p["name"] != "default"]
        }
    except Exception as e:
        return {"projects": ["ai-coroner-demo"], "error": str(e)}


if __name__ == "__main__":
    mcp.run()