import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.resolve()

WORKSPACE_DIR = BASE_DIR / "workspace"
SKILLS_DIR = BASE_DIR / "skills"

WORKSPACE_DIR.mkdir(exist_ok=True)
SKILLS_DIR.mkdir(exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set in the .env file."
    )

MODEL = "openai/gpt-oss-120b"

MAX_AGENT_STEPS = 20

MAX_TOOL_OUTPUT = 12_000

KEEP_RECENT_MESSAGES = 12

SUMMARIZE_AFTER_MESSAGES = 20

MAX_SUMMARY_CHARS = 12_000
