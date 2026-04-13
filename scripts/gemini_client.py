import os
import sys

from env_loader import load_project_env


load_project_env(__file__)


def get_gemini_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is required.")
        print("Set it in your shell or add it to the repository .env file.")
        sys.exit(1)
    return api_key


def get_genai_client():
    from google import genai

    return genai.Client(api_key=get_gemini_api_key())


def iter_response_parts(response):
    if hasattr(response, "parts") and response.parts:
        for part in response.parts:
            yield part
        return

    candidates = getattr(response, "candidates", None) or []
    for candidate in candidates:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            yield part
