import asyncio
import os
from agents import Agent, Runner, function_tool, set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Disable tracing
set_tracing_disabled(disabled=True)

model = "gemini/gemini-2.0-flash"
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not found in .env file")
    exit(1)

# Sample logs
sample_logs = """
2024-10-21 14:23:45 ERROR Database connection failed
2024-10-21 14:23:46 WARN Retry attempt 1 of 3
2024-10-21 14:23:48 ERROR Database connection failed
2024-10-21 14:23:49 WARN Retry attempt 2 of 3
2024-10-21 14:23:51 ERROR Database connection failed
2024-10-21 14:23:52 ERROR Maximum retries reached
"""
# Ask the AI to analyze it
prompt = f"""You are a DevOps engineer analyzing application logs.
Analyze this log and explain what's happening:
{sample_logs}
Provide a brief analysis and suggest what might be wrong."""


# Tool
@function_tool
def sample_dummy_log():
    """Returns recent application logs."""
    return sample_logs


async def main():
    agent = Agent(
        name="DevOps logs analyzer",
        instructions="You are a DevOps engineer that analyzes logs and explains system failures.",
        model=LitellmModel(model=model, api_key=api_key),
        tools=[sample_dummy_log],
    )

    print("Analyzing logs with AI...")
    print("-" * 50)

    result = await Runner.run(
        agent,
        input="Fetch the logs and analyze what caused the failure."
    )

    print(result.final_output)
    print("-" * 50)
    print("✓ Setup successful! Your environment is ready.")


if __name__ == "__main__":
    asyncio.run(main())
