# src/tools/log_tools.py

import os
from pathlib import Path
from agents import function_tool
from ..config import Config


@function_tool
def read_log_file(filename: str) -> str:
    """Read the full contents of a log file from the logs directory.
    Use this when you need to analyze the complete log.
    Input should be just the filename, e.g. 'app.log'
    """
    log_path = Path(Config.LOG_DIRECTORY) / filename

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        line_count = content.count('\n') + 1
        size_kb = os.path.getsize(log_path) / 1024

        return (
            f"File: {filename}\n"
            f"Size: {size_kb:.2f} KB | Lines: {line_count}\n"
            f"{'=' * 40}\n\n"
            f"{content}"
        )

    except FileNotFoundError:
        return f"Error: '{filename}' not found in {Config.LOG_DIRECTORY}/"
    except PermissionError:
        return f"Error: Permission denied reading '{filename}'"
    except Exception as e:
        return f"Error reading '{filename}': {str(e)}"


@function_tool
def list_log_files() -> str:
    """List all available log files in the logs directory.
    Use this first when the user has not specified a filename.
    """
    log_dir = Path(Config.LOG_DIRECTORY)

    if not log_dir.exists():
        return f"Error: Directory '{Config.LOG_DIRECTORY}' does not exist"

    try:
        files = sorted(
            f for f in log_dir.iterdir()
            if f.is_file() and f.suffix == '.log'
        )

        if not files:
            return f"No .log files found in {Config.LOG_DIRECTORY}/"

        result = f"Available log files in {Config.LOG_DIRECTORY}/:\n\n"
        for f in files:
            size_kb = f.stat().st_size / 1024
            result += f"  - {f.name} ({size_kb:.2f} KB)\n"

        return result

    except Exception as e:
        return f"Error listing files: {str(e)}"


@function_tool
def search_logs(filename: str, search_term: str) -> str:
    """Search for a specific term in a log file and return matching lines.
    Use this when looking for specific errors, keywords, or patterns.
    Input: filename e.g. 'app.log', search_term e.g. 'ERROR' or 'timeout'
    """
    log_path = Path(Config.LOG_DIRECTORY) / filename

    try:
        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        matches = [
            f"Line {i}: {line.rstrip()}"
            for i, line in enumerate(lines, 1)
            if search_term.lower() in line.lower()
        ]

        if not matches:
            return f"No matches for '{search_term}' in {filename}"

        return (
            f"Found {len(matches)} matches for '{search_term}' in {filename}:\n\n"
            + "\n".join(matches)
        )

    except FileNotFoundError:
        return f"Error: '{filename}' not found"
    except Exception as e:
        return f"Error searching '{filename}': {str(e)}"


@function_tool
def save_summary(summary: str) -> str:
    """Save the final analysis summary to Summary.md.
    Always call this tool after completing your log analysis.
    Input should be your complete analysis as a string.
    """
    try:
        with open('Summary.md', 'w', encoding='utf-8') as f:
            f.write("## Log Analysis Summary\n\n")
            f.write(summary)
        return "Summary successfully saved to Summary.md"
    except Exception as e:
        return f"Error saving summary: {str(e)}"


def get_log_tools():
    """Return all log analysis tools."""
    return [list_log_files, read_log_file, search_logs, save_summary]