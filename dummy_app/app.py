import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import litellm
import time
import random
from arize.otel import register as arize_register
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from dotenv import load_dotenv

from dummy_app.config import APP_NAME, SYSTEM_PROMPT
from dummy_app.questions import QUESTIONS

load_dotenv()

ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Register with BOTH Arize cloud AND local Phoenix
import phoenix as px
px.launch_app()

from phoenix.otel import register as phoenix_register
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from arize.otel import register as arize_register

# Phoenix tracer
phoenix_provider = phoenix_register(
    project_name=APP_NAME,
    auto_instrument=False
)

# Arize cloud tracer
arize_provider = arize_register(
    space_id=ARIZE_SPACE_ID,
    api_key=ARIZE_API_KEY,
    project_name=APP_NAME,
)

# Instrument LiteLLM with Phoenix
LiteLLMInstrumentor().instrument(tracer_provider=phoenix_provider)

def ask_question(question: str):
    """Send one question to ShopBot."""
    try:
        response = litellm.completion(
            model="groq/llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]
        )
        answer = response.choices[0].message.content
        print(f"Q: {question[:60]}")
        print(f"A: {answer[:80]}...\n")
        return answer
    except Exception as e:
        print(f"Error: {e}\n")
        return None

def run_continuous(interval_seconds: int = 10):
    print("ShopBot LIVE - sending questions continuously...")
    print(f"   New question every {interval_seconds} seconds")
    print("   Press Ctrl+C to stop\n")
    count = 0
    while True:
        count += 1
        question = random.choice(QUESTIONS)
        print(f"[{count}] ", end="")
        ask_question(question)
        time.sleep(interval_seconds)

def run_once():
    print("Running ShopBot once...\n")
    for i, question in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] ", end="")
        ask_question(question)
    print("Done! Traces logged to Phoenix and Arize cloud.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--interval", type=int, default=10)
    args = parser.parse_args()
    if args.live:
        run_continuous(interval_seconds=args.interval)
    else:
        run_once()