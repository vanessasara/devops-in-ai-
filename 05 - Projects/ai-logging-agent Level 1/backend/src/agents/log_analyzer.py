# src/agents/log_analyzer.py

from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

from ..config import Config
from ..tools import get_log_tools
from ..utils.response import format_output

set_tracing_disabled(disabled=True)


class LogAnalyzerAgent:
    """
    Level 1 AI Logging Agent.

    Capabilities:
    - List available log files
    - Read and analyze log file contents
    - Search logs for specific terms or patterns
    - Save analysis summary to Summary.md

    Limitations:
    - No routing decisions (Level 2)
    - No automated actions like service restarts
    - No multi-source integration (Level 3)
    - No persistent memory across sessions
    """

    def __init__(self):
        self.agent = Agent(
            name="DevOps logs analyzer",
            instructions=Config.get_instructions(),
            model=LitellmModel(
                model=Config.GEMINI_MODEL,
                api_key=Config.GEMINI_API_KEY,
            ),
            tools=get_log_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        """
        Run the agent on a single user query and return the response.
        The Runner handles the full agentic loop internally:
        - Tool selection and execution
        - Result observation
        - Final response generation
        """
        try:
            result = await Runner.run(
                self.agent,
                input=user_input,
            )
            return format_output(result)

        except Exception as e:
            return f"Error processing query: {str(e)}"