import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Auto-detect provider if not explicitly set
if not LLM_PROVIDER:
    if GROQ_API_KEY:
        LLM_PROVIDER = "groq"
    elif GEMINI_API_KEY:
        LLM_PROVIDER = "gemini"
    elif ANTHROPIC_API_KEY:
        LLM_PROVIDER = "anthropic"
    elif OPENAI_API_KEY:
        LLM_PROVIDER = "openai"
    else:
        LLM_PROVIDER = "groq"  # default

# Default models per provider
DEFAULT_MODELS = {
    "groq": "openai/gpt-oss-120b",  # Best free model on Groq: 120B parameter open-weights model
    "gemini": "gemini-2.0-flash",
    "anthropic": "claude-3-7-sonnet-20250219",
    "openai": "gpt-4o-mini",
}

MODEL_NAME = os.getenv("MODEL_NAME") or DEFAULT_MODELS.get(LLM_PROVIDER, "openai/gpt-oss-120b")
RECALL_PASS_THRESHOLD = float(os.getenv("RECALL_PASS_THRESHOLD", "0.7"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
PORT = int(os.getenv("PORT", "5007"))


