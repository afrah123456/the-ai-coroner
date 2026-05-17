import streamlit as st
import os
import time
import httpx
import pandas as pd
from datetime import datetime
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load secrets from Streamlit Cloud or local .env
try:
    os.environ["ARIZE_API_KEY"] = st.secrets["ARIZE_API_KEY"]
    os.environ["ARIZE_SPACE_ID"] = st.secrets["ARIZE_SPACE_ID"]
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
    os.environ["SLACK_WEBHOOK_URL"] = st.secrets["SLACK_WEBHOOK_URL"]
    os.environ["ALERT_THRESHOLD"] = st.secrets["ALERT_THRESHOLD"]
    os.environ["PHOENIX_API_KEY"] = st.secrets["PHOENIX_API_KEY"]
    os.environ["PHOENIX_SPACE_URL"] = st.secrets["PHOENIX_SPACE_URL"]
except:
    from dotenv import load_dotenv

    load_dotenv()

# Page config
st.set_page_config(
    page_title="The AI Coroner",
    page_icon="🔬",
    layout="wide"
)

PHOENIX_BASE_URL = "http://localhost:6006"

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .stButton>button {
        background-color: #ff4b4b;
        color: white;
        border-radius: 8px;
        padding: 0.5em 2em;
        font-size: 1.1em;
        border: none;
        width: 100%;
    }
    .stButton>button:hover { background-color: #cc0000; }
    .metric-card {
        background: #1e2130;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2e3250;
    }
    .metric-value { font-size: 2.5em; font-weight: bold; color: white; }
    .metric-label { font-size: 0.9em; color: #888; margin-top: 4px; }
    .header-bar {
        background: linear-gradient(90deg, #1a1a2e, #16213e);
        padding: 20px 30px;
        border-radius: 12px;
        margin-bottom: 20px;
        border: 1px solid #2e3250;
    }
    .step-box {
        background: #1e2130;
        border-radius: 10px;
        padding: 15px 20px;
        margin: 8px 0;
        border-left: 4px solid #ff4b4b;
    }
</style>
""", unsafe_allow_html=True)


# Helper functions
def get_available_projects() -> list[str]:
    # Try local Phoenix first
    try:
        response = httpx.get(f"{PHOENIX_BASE_URL}/v1/projects", timeout=2)
        if response.status_code == 200:
            projects = response.json().get("data", [])
            names = [p["name"] for p in projects if p["name"] != "default"]
            if names:
                return names
    except:
        pass

    # Try Arize cloud Phoenix
    try:
        phoenix_space_url = os.getenv("PHOENIX_SPACE_URL", "https://app.phoenix.arize.com/s/shahabuddin-af")
        phoenix_api_key = os.getenv("PHOENIX_API_KEY", "")
        response = httpx.get(
            f"{phoenix_space_url}/v1/projects",
            headers={"Authorization": f"Bearer {phoenix_api_key}"},
            timeout=5
        )
        if response.status_code == 200:
            projects = response.json().get("data", [])
            names = [p["name"] for p in projects if p["name"] != "default"]
            if names:
                return names
    except:
        pass

    return ["ai-coroner-demo"]


def run_autopsy(project_name: str):
    from agent.fetcher.fetcher_agent import fetch_and_filter_traces
    from agent.analyzer.analyzer_agent import analyze_failures
    from agent.reporter.reporter_agent import generate_report
    from agent.history import save_result
    from agent.alerts import send_slack_alert
    from agent.fetcher.arize_client import get_traces

    # Debug — show raw spans
    spans = get_traces(project_name)
    st.write(f"Debug: fetched {len(spans)} raw spans")
    if spans:
        attrs = spans[0].get("attributes", {})
        st.write(f"Debug first span keys: {list(attrs.keys())[:5]}")
        st.write(f"Debug input sample: {str(attrs.get('llm.input_messages.1.message.content', 'NOT FOUND'))[:100]}")
        st.write(f"Debug output sample: {str(attrs.get('llm.output_messages.0.message.content', 'NOT FOUND'))[:100]}")

    fetcher_results = fetch_and_filter_traces(project_name)
    analysis = analyze_failures(fetcher_results)
    report = generate_report(analysis)
    save_result(analysis, project_name)
    send_slack_alert(analysis, project_name, report)
    return analysis, report

# Header
st.markdown("""
<div class="header-bar">
    <h1 style="color:white; margin:0;">🔬 The AI Coroner</h1>
    <p style="color:#888; margin:0;">Autonomous LLM Diagnostic Agent — detect, diagnose, and fix AI failures in real time</p>
</div>
""", unsafe_allow_html=True)

# Step 1: Select App
st.markdown("### Step 1 — Select the LLM app to monitor")
projects = get_available_projects()

cols = st.columns(len(projects) if len(projects) <= 4 else 4)
selected_project = st.session_state.get("selected_project", projects[0])

for i, project in enumerate(projects):
    with cols[i % 4]:
        is_selected = selected_project == project
        if st.button(
                f"{'✅ ' if is_selected else ''}{project}",
                key=f"proj_{project}",
                use_container_width=True
        ):
            st.session_state["selected_project"] = project
            selected_project = project
            st.session_state.pop("analysis", None)

st.divider()

# Step 2: Run Autopsy
st.markdown("### Step 2 — Run the autopsy")

col_btn, col_info = st.columns([1, 3])
with col_btn:
    run_clicked = st.button("🔬 Run Autopsy", use_container_width=True)

with col_info:
    st.info(
        f"Monitoring: **{selected_project}** — The AI Coroner will fetch live traces, detect failures, and generate a diagnosis report.")

if run_clicked:
    with st.spinner("🔬 Performing autopsy — fetching traces, clustering failures, generating report..."):
        analysis, report = run_autopsy(selected_project)
        st.session_state["analysis"] = analysis
        st.session_state["report"] = report
        st.session_state["last_run"] = datetime.now().strftime("%H:%M:%S")
    st.success("✅ Autopsy complete! Scroll down to see results.")

st.divider()

# Step 3: Results
if "analysis" in st.session_state:
    analysis = st.session_state["analysis"]
    report = st.session_state["report"]
    last_run = st.session_state.get("last_run", "")

    st.markdown(f"### Step 3 — Autopsy Results *(last run: {last_run})*")

    # Health banner
    if analysis["failure_rate"] == 0:
        st.success("🟢 Your LLM app is healthy — no failures detected!")
    elif analysis["failure_rate"] < 20:
        st.success(f"🟢 Healthy — {analysis['failure_rate']}% failure rate")
    elif analysis["failure_rate"] < 50:
        st.warning(f"🟡 Needs Attention — {analysis['failure_rate']}% failure rate detected")
    else:
        st.error(f"🔴 Critical — {analysis['failure_rate']}% failure rate! Immediate action required.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Historical trend chart
    from agent.history import load_history

    history = load_history(selected_project)

    if len(history) > 1:
        st.subheader("📈 Failure Rate Over Time")
        trend_data = pd.DataFrame([
            {
                "Time": h["timestamp"][11:16],
                "Failure Rate %": h["failure_rate"]
            }
            for h in history[-20:]
        ])
        st.line_chart(trend_data.set_index("Time"))
        st.divider()

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analysis['total_interactions']}</div>
            <div class="metric-label">Total Interactions</div>
        </div>""", unsafe_allow_html=True)
    with m2:
        color = "#ff4b4b" if analysis['total_failures'] > 0 else "#00cc88"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color:{color}">{analysis['total_failures']}</div>
            <div class="metric-label">Failures Detected</div>
        </div>""", unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{analysis['failure_rate']}%</div>
            <div class="metric-label">Failure Rate</div>
        </div>""", unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(analysis['clusters'])}</div>
            <div class="metric-label">Failure Patterns Found</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart + Clusters
    if analysis["clusters"]:
        left, right = st.columns([1, 2])

        with left:
            st.markdown("#### 📈 Failure Breakdown")
            chart_data = pd.DataFrame([
                {"Pattern": c["pattern"]["name"], "Count": c["count"]}
                for c in analysis["clusters"]
            ])
            st.bar_chart(chart_data.set_index("Pattern"))

        with right:
            st.markdown("#### 🚨 Diagnosed Failure Patterns")
            for i, cluster in enumerate(analysis["clusters"], 1):
                pattern = cluster["pattern"]
                with st.expander(
                        f"#{i}  {pattern['name']}  —  {cluster['count']} occurrence{'s' if cluster['count'] > 1 else ''}",
                        expanded=i == 1
                ):
                    st.error(f"**Root Cause:** {pattern['description']}")
                    for j, ex in enumerate(cluster["examples"], 1):
                        st.markdown(f"**Example {j}:**")
                        st.markdown(f"🧑 User: `{ex['input']}`")
                        st.markdown(f"🤖 Bot: _{ex['output'][:180]}..._")
                        if j < len(cluster["examples"]):
                            st.divider()
                    st.success(f"💊 **Fix:** {cluster['fix']}")
    else:
        st.success("✅ No failure patterns detected!")

    st.divider()

    # Live monitoring
    st.markdown("#### 🔴 Live Monitoring")
    col_toggle, col_interval = st.columns([1, 2])
    with col_toggle:
        live = st.toggle("Enable auto-refresh", value=False)
    with col_interval:
        interval = st.slider("Refresh every (seconds)", 10, 60, 15)

    if live:
        st.info(f"🔄 Auto-refreshing every {interval} seconds...")
        time.sleep(interval)
        analysis, report = run_autopsy(selected_project)
        st.session_state["analysis"] = analysis
        st.session_state["report"] = report
        st.session_state["last_run"] = datetime.now().strftime("%H:%M:%S")
        st.rerun()

    st.divider()

    # Download report
    st.markdown("#### 📄 Download Autopsy Report")
    st.download_button(
        label="⬇️ Download Full Report (.md)",
        data=report,
        file_name=f"autopsy_{selected_project}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )

    with st.expander("👁️ Preview Report"):
        st.markdown(report)

else:
    st.markdown("### Step 3 — Results will appear here")
    st.markdown("""
    <div class="step-box">🔍 Click <b>Run Autopsy</b> above to start analyzing your LLM app</div>
    <div class="step-box">📊 The AI Coroner will fetch live traces from Arize Phoenix</div>
    <div class="step-box">🧠 Failures will be clustered and diagnosed automatically</div>
    <div class="step-box">📄 A full autopsy report will be generated with prescribed fixes</div>
    """, unsafe_allow_html=True)