import os
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
ARIZE_API_KEY = os.getenv("ARIZE_API_KEY")
ARIZE_SPACE_ID = os.getenv("ARIZE_SPACE_ID")

APP_NAME = "ai-coroner-demo"
MODEL_NAME = "gemini-1.5-flash"

SYSTEM_PROMPT = """You are a customer support assistant for an online 
store called ShopBot. Answer questions about orders, returns, shipping, 
and payments. If a question is out of scope, politely say so."""