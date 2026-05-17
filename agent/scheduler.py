import schedule
import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.orchestrator import run_autopsy
from datetime import datetime

def scheduled_job(project_name: str = "ai-coroner-demo"):
    """Run autopsy and print summary."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running scheduled autopsy...")
    report = run_autopsy(project_name)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Scheduled autopsy complete!\n")

def run_scheduler(
    project_name: str = "ai-coroner-demo",
    interval_minutes: int = 60
):
    """Run the scheduler continuously."""
    print(f"Scheduler started - running autopsy every {interval_minutes} minutes")
    print(f"Monitoring project: {project_name}")
    print("Press Ctrl+C to stop\n")

    # Run immediately on start
    scheduled_job(project_name)

    # Schedule recurring runs
    schedule.every(interval_minutes).minutes.do(
        scheduled_job, project_name=project_name
    )

    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="ai-coroner-demo")
    parser.add_argument("--interval", type=int, default=60)
    args = parser.parse_args()
    run_scheduler(project_name=args.project, interval_minutes=args.interval)