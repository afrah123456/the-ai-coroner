import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import litellm
import time
import random
from phoenix.otel import register as phoenix_register
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from dotenv import load_dotenv

from dummy_app.config import APP_NAME, SYSTEM_PROMPT
from dummy_app.questions import QUESTIONS

load_dotenv()

PHOENIX_API_KEY = os.getenv("PHOENIX_API_KEY")
PHOENIX_SPACE_URL = os.getenv("PHOENIX_SPACE_URL", "https://app.phoenix.arize.com/s/shahabuddin-af")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# Send traces to Phoenix cloud
os.environ["PHOENIX_API_KEY"] = PHOENIX_API_KEY
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = f"{PHOENIX_SPACE_URL}"

tracer_provider = phoenix_register(
    project_name=APP_NAME,
    auto_instrument=True,
    endpoint=f"{PHOENIX_SPACE_URL}/v1/traces",
    headers={"Authorization": f"Bearer {PHOENIX_API_KEY}"}
)

LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)

def ask_question(question: str):
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
    print(f"   Logging to Phoenix cloud: {PHOENIX_SPACE_URL}")
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
    print(f"   Logging to Phoenix cloud: {PHOENIX_SPACE_URL}\n")
    for i, question in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] ", end="")
        ask_question(question)
    print("Done! Check app.phoenix.arize.com for traces.")

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