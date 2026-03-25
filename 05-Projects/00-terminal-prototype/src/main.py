import asyncio
from .agents import LogAnalyzerAgent
from .config import Config

def main():
    Config.validate()
    print("=" * 50)
    print("  AI Log Analyzer — Terminal")
    print("  Type 'quit' to exit, 'clear' to reset")
    print("=" * 50)

    agent = LogAnalyzerAgent()

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["quit", "exit"]:
                break
            if user_input.lower() == "clear":
                agent = LogAnalyzerAgent()
                print("Agent reset.")
                continue

            response = asyncio.run(agent.process_query(user_input))
            print(f"\nAgent: {response}")

        except KeyboardInterrupt:
            print("\nType 'quit' to exit.")
        except EOFError:
            break

if __name__ == "__main__":
    main()