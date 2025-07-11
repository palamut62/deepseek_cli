import os
from pathlib import Path

try:
    from dotenv import load_dotenv  # type: ignore

    # load .env file from current working directory if present
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    # python-dotenv not installed; continue without loading .env
    pass

# DeepSeek API configuration loaded from environment variables for flexibility
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-coder")
DEEPSEEK_API_BASE = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")

# fallback check to warn developer when key is missing
if not DEEPSEEK_API_KEY:
    # avoid noisy output in production, only warn in dev mode
    if os.getenv("PYTHON_ENV", "development") == "development":
        print("[WARN][config] DEEPSEEK_API_KEY environment variable is not set. API calls will fail.") 