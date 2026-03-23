from agents import Agent, Runner, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel

from ..config import Config
from ..tools import get_all_tools

set_tracing_disabled(disabled=True)


class LogAnalyzerAgent:
    def __init__(self):
        self.agent = Agent(
            name="DevOps incident responder",
            instructions=Config.get_instructions(),
            model=LitellmModel(
                model=Config.GEMINI_MODEL,
                api_key=Config.GEMINI_API_KEY,
            ),
            tools=get_all_tools(),
        )

    async def process_query(self, user_input: str) -> str:
        try:
            result = await Runner.run(self.agent, input=user_input)
            output = getattr(result, "final_output", None)
            return str(output).strip() if output else "No response."
        except Exception as e:
            return f"Error: {e}"
