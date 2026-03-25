import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini/gemini-3-flash-preview")
    LOG_DIRECTORY  = os.getenv("LOG_DIRECTORY", "logs")

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY not set in .env")
        if not os.path.exists(cls.LOG_DIRECTORY):
            os.makedirs(cls.LOG_DIRECTORY)

    @classmethod
    def get_instructions(cls) -> str:
        return """You are a DevOps expert specializing in log analysis.
- Analyze logs to identify errors, warnings, and patterns
- Explain issues in clear, concise language
- Use list_log_files first if no filename is given
- Use read_log_file to read full contents
- Use search_logs for specific patterns
- Always call save_summary after a full analysis"""