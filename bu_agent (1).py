import asyncio
from browser_use import Agent, Browser, ChatOllama

llm = ChatOllama(
    model="llama3.2",
    # Bigger context so the page's element list isn't cut off.
    # (If your version rejects this argument, remove the line.)
    ollama_options={"num_ctx": 16000},
)

browser = Browser(headless=False)   # keep False so you can watch it work

TASK = """
Go directly to https://www.bing.com/search?q=HP+laptop+12th+gen+core+i5+16GB+512GB
Look at the first 5 non-sponsored results.
List each one with its name, price (if shown) and link.
Then finish.
"""

async def main():
    agent = Agent(
        task=TASK,
        llm=llm,
        browser=browser,
        use_vision=False,       # llama3.2 cannot read screenshots
        max_failures=3,         # stop after 3 errors instead of looping
    )
    result = await agent.run(max_steps=12)
    print("\n===== FINAL RESULT =====")
    print(result.final_result())

asyncio.run(main())