import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()

server = MCPServerStdio('python', ["server.py"])  
agent = Agent('openai:gpt-4o', toolsets=[server])  

async def main():
    async with agent:
        message_history = []
        while True:
            query = input("\nAsk me about cogents jobs (or type 'q' to exit): ")
            if query.lower() == "q":
                break

            result = await agent.run(query, message_history=message_history)
            print("\n", result.output)

            message_history.extend(result.new_messages())
            if len(message_history) > 12:
                message_history.pop(0)

if __name__ == '__main__':
    asyncio.run(main())
