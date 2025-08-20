import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()

server = MCPServerStdio('python', ["server.py"])
agent = Agent('openai:gpt-4o-mini', toolsets=[server])

async def main():
    async with agent:  
        result = await agent.run('How many days between 2000-01-01 and 2025-03-18?')
    print(result.output)
    
if __name__ == "__main__":
    asyncio.run(main())
