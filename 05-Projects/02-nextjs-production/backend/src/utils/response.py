# src/utils/response.py


def format_output(result) -> str:
    """Extract and clean the final output from a Runner result.

    Runner.run() returns a RunResult object. final_output is usually
    a string but can be None if the agent did not produce text output
    (e.g. only called tools). This handles both cases cleanly.
    """
    if result is None:
        return "No response received."

    output = getattr(result, 'final_output', None)

    if output is None:
        return "Agent completed without producing a text response."

    if isinstance(output, str):
        return output.strip()

    return str(output).strip()