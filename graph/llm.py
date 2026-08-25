import os
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel
from config import (
    LLM_PROVIDER,
    MODEL_NAME,
    GROQ_API_KEY,
    GEMINI_API_KEY,
    ANTHROPIC_API_KEY,
    OPENAI_API_KEY,
)


def get_llm(temperature: float = 0.0, max_tokens: Optional[int] = None) -> BaseChatModel:
    """
    Factory function to get the configured chat LLM instance based on environment settings.
    Defaults to Groq (free tier) if GROQ_API_KEY is available.
    """
    provider = LLM_PROVIDER.lower()

    if provider == "groq":
        api_key = GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY is not set. Get a free API key at https://console.groq.com "
                "and set it in your .env file."
            )
        from langchain_groq import ChatGroq

        kwargs = {"groq_api_key": api_key, "model_name": MODEL_NAME, "temperature": temperature}
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        return ChatGroq(**kwargs)

    elif provider in ("gemini", "google"):
        api_key = GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set. Get a free API key at https://aistudio.google.com "
                "and set it in your .env file."
            )
        from langchain_google_genai import ChatGoogleGenerativeAI

        kwargs = {"google_api_key": api_key, "model": MODEL_NAME, "temperature": temperature}
        if max_tokens:
            kwargs["max_output_tokens"] = max_tokens
        return ChatGoogleGenerativeAI(**kwargs)

    elif provider == "anthropic":
        api_key = ANTHROPIC_API_KEY or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY is not set. Please set it in your .env file."
            )
        from langchain_anthropic import ChatAnthropic

        kwargs = {"anthropic_api_key": api_key, "model_name": MODEL_NAME, "temperature": temperature}
        if max_tokens:
            kwargs["max_tokens_to_sample"] = max_tokens
        return ChatAnthropic(**kwargs)

    elif provider in ("openai", "openrouter"):
        api_key = OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please set it in your .env file."
            )
        from langchain_openai import ChatOpenAI

        kwargs = {"api_key": api_key, "model": MODEL_NAME, "temperature": temperature}
        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        return ChatOpenAI(**kwargs)

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{provider}'. "
            f"Supported providers: 'groq', 'gemini', 'anthropic', 'openai'."
        )


def clean_llm_output(content: str) -> str:
    """Strip <think>...</think> reasoning blocks if produced by reasoning models."""
    import re
    if not isinstance(content, str):
        content = str(content)
    # Remove thinking tags and enclosed text
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", content)
    return cleaned.strip()

