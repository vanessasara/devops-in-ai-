import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini/gemini-3-flash-preview")
    LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
    K8S_ENABLED = os.getenv("K8S_ENABLED", "false").lower() == "true"

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        if not os.path.exists(cls.LOG_DIRECTORY):
            os.makedirs(cls.LOG_DIRECTORY)

    @classmethod
    def get_instructions(cls) -> str:
        prompt_file = Path(__file__).parent.parent / "system_prompt.txt"
        if prompt_file.exists():
            return prompt_file.read_text(encoding="utf-8")
        return "You are a DevOps expert analyzing logs."
