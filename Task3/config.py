from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from the nearest dotenv file (if any) or the environment
load_dotenv(find_dotenv() or None)

# Prefer environment variables from the system or workspace-level dotenv
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
DEFAULT_TONE = os.getenv("DEFAULT_TONE", "beginner")

PROMPT_JSON_SCHEMA = {
    "summary": "string",
    "good_thing": "string",
    "improvement": "string",
    "verdict": "Aggressive | Balanced | Conservative",
}
