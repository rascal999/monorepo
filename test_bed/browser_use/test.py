import asyncio
from browser_use import Agent
from langchain_ollama import ChatOllama


async def run_search() -> str:
    agent = Agent(
        task="Search for a 'browser use' post on the r/LocalLLaMA subreddit and open it.",
        llm=ChatOllama(
            # model="qwen2.5:32b-instruct-q4_K_M",
            model="deepseek-r1:14b"
        ),
    )

    result = await agent.run()
    return result


async def main():
    result = await run_search()
    print("\n\n", result)


if __name__ == "__main__":
    asyncio.run(main())
