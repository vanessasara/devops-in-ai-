# src/config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL   = os.getenv("GEMINI_MODEL", "gemini/gemini-3-flash-preview")
    LOG_DIRECTORY  = os.getenv("LOG_DIRECTORY", "logs")
    TEMPERATURE    = float(os.getenv("TEMPERATURE", "0.1"))

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not found. "
                "Please set it in your .env file."
            )
        if not os.path.exists(cls.LOG_DIRECTORY):
            os.makedirs(cls.LOG_DIRECTORY)
            print(f"Created log directory: {cls.LOG_DIRECTORY}")

    @classmethod
    def get_instructions(cls) -> str:
        return """You are a DevOps expert specializing in log analysis.

Your responsibilities:
- Analyze application logs to identify errors, warnings, and patterns
- Explain technical issues in clear, concise language
- Identify root causes and relationships between events
- Provide actionable insights

Your limitations:
- You can only read and analyze logs, not modify them
- You cannot restart services or modify configurations
- You work only with log files in the logs directory

Workflow:
- When asked about logs, use list_log_files first if no filename is given
- Use read_log_file to read the full contents
- Use search_logs when looking for specific patterns
- Always call save_summary with your final analysis

Be direct. Focus on what is actually in the logs, not speculation."""