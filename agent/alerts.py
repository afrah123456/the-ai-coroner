import os
import httpx
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
ALERT_THRESHOLD = float(os.getenv("ALERT_THRESHOLD", 30))


def send_slack_alert(analysis: dict, project_name: str, report: str = None):
    """Send a Slack alert when failure rate exceeds threshold."""

    if not SLACK_WEBHOOK_URL:
        print("No Slack webhook configured, skipping alert")
        return

    failure_rate = analysis["failure_rate"]

    if failure_rate < ALERT_THRESHOLD:
        print(f"Failure rate {failure_rate}% below threshold {ALERT_THRESHOLD}%, no alert sent")
        return

    # Build health emoji
    if failure_rate < 20:
        health_emoji = ":large_green_circle:"
        health = "Healthy"
    elif failure_rate < 50:
        health_emoji = ":large_yellow_circle:"
        health = "Needs Attention"
    else:
        health_emoji = ":red_circle:"
        health = "Critical"

    # Build cluster summary with fixes
    clusters_text = ""
    for c in analysis["clusters"]:
        clusters_text += f"• *{c['pattern']['name']}* — {c['count']} occurrences\n"
        clusters_text += f"  _Fix: {c['fix'][:100]}..._\n\n"

    if not clusters_text:
        clusters_text = "No failure patterns detected"

    # Build Slack alert message
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🔬 AI Coroner — Autopsy Alert"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Project:*\n`{project_name}`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Health:*\n{health_emoji} {health}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Failure Rate:*\n`{failure_rate}%`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total Interactions:*\n`{analysis['total_interactions']}`"
                    }
                ]
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Failure Patterns & Prescribed Fixes:*\n{clusters_text}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f":warning: *Alert:* Failure rate `{failure_rate}%` exceeded threshold of `{ALERT_THRESHOLD}%`"
                }
            }
        ]
    }

    try:
        # Send the alert message
        response = httpx.post(
            SLACK_WEBHOOK_URL,
            json=message,
            timeout=10
        )
        if response.status_code == 200:
            print("Slack alert sent successfully!")
        else:
            print(f"Slack alert failed: {response.status_code}")

        # Send the full report as chunks
        if report:
            chunks = [report[i:i + 2900] for i in range(0, len(report), 2900)]

            for i, chunk in enumerate(chunks):
                part_message = {
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Full Autopsy Report (Part {i + 1}/{len(chunks)}):*\n```{chunk}```"
                            }
                        }
                    ]
                }
                httpx.post(
                    SLACK_WEBHOOK_URL,
                    json=part_message,
                    timeout=10
                )
                print(f"Report part {i + 1}/{len(chunks)} sent!")

    except Exception as e:
        print(f"Slack alert error: {e}")


if __name__ == "__main__":
    # Test the alert
    test_analysis = {
        "total_interactions": 15,
        "total_failures": 6,
        "failure_rate": 40.0,
        "clusters": [
            {
                "pattern": {"name": "Out of Scope", "description": "User asked something unrelated"},
                "count": 3,
                "fix": "Improve the system prompt to explicitly list what topics are in and out of scope."
            },
            {
                "pattern": {"name": "Gibberish Input", "description": "User sent random characters"},
                "count": 2,
                "fix": "Add an input validation layer that detects and rejects gibberish."
            },
            {
                "pattern": {"name": "Aggressive Input", "description": "User sent aggressive messages"},
                "count": 1,
                "fix": "Add a tone detection layer for aggressive inputs."
            },
        ]
    }
    test_report = """
# AI Coroner — Autopsy Report
**Generated:** 2026-05-17
**Project:** ai-coroner-demo

## Summary
| Metric | Value |
|--------|-------|
| Total Interactions | 15 |
| Total Failures | 6 |
| Failure Rate | 40.0% |
| Failure Clusters | 3 |

## Failure #1: Out of Scope
**Occurrences:** 3
**Diagnosis:** User asked something completely unrelated
**Fix:** Improve the system prompt to list in/out of scope topics.

## Failure #2: Gibberish Input
**Occurrences:** 2
**Diagnosis:** User sent random characters
**Fix:** Add input validation layer.

## Failure #3: Aggressive Input
**Occurrences:** 1
**Diagnosis:** User sent aggressive messages
**Fix:** Add tone detection layer.

## Overall Health: Needs Attention
Significant failure patterns detected. Apply prescribed fixes and re-evaluate.
"""
    send_slack_alert(test_analysis, "ai-coroner-demo", test_report)