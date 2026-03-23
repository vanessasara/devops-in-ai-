def format_output(result) -> str:
    if result is None:
        return "No response received."
    output = getattr(result, "final_output", None)
    if output is None:
        return "Agent completed without producing a text response."
    return str(output).strip()
