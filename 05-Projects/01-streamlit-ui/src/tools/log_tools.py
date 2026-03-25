import os
from pathlib import Path
from agents import function_tool
from ..config import Config

@function_tool
def list_log_files() -> str:
    """List all available log files. Use this first when no filename is given."""
    files = sorted(Path(Config.LOG_DIRECTORY).glob("*.log"))
    if not files:
        return "No .log files found."
    return "Available files:\n" + "\n".join(
        f"  - {f.name} ({f.stat().st_size / 1024:.2f} KB)" for f in files
    )

@function_tool
def read_log_file(filename: str) -> str:
    """Read the full contents of a log file. Input: filename e.g. app.log"""
    path = Path(Config.LOG_DIRECTORY) / filename
    try:
        content = path.read_text(encoding="utf-8")
        lines = content.count("\n") + 1
        return f"File: {filename} | {lines} lines\n\n{content}"
    except FileNotFoundError:
        return f"Error: '{filename}' not found"
    except Exception as e:
        return f"Error: {e}"

@function_tool
def search_logs(filename: str, search_term: str) -> str:
    """Search for a term in a log file. Input: filename, search_term e.g. ERROR"""
    path = Path(Config.LOG_DIRECTORY) / filename
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
        matches = [
            f"Line {i}: {line}"
            for i, line in enumerate(lines, 1)
            if search_term.lower() in line.lower()
        ]
        if not matches:
            return f"No matches for '{search_term}' in {filename}"
        return f"Found {len(matches)} matches:\n\n" + "\n".join(matches)
    except FileNotFoundError:
        return f"Error: '{filename}' not found"

@function_tool
def save_summary(summary: str) -> str:
    """Save the final analysis to Summary.md. Always call this after analysis."""
    Path("Summary.md").write_text(
        f"## Log Analysis Summary\n\n{summary}", encoding="utf-8"
    )
    return "Summary saved to Summary.md"

def get_log_tools():
    return [list_log_files, read_log_file, search_logs, save_summary]