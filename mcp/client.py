import asyncio
from pydantic_ai import Agent
from dotenv import load_dotenv
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()

mcp_servers = [MCPServerStdio("python", ["server.py"])]

system_prompt = """
You are a helpful assistant specialized in CogentLabs job applications and candidates.

follow the steps if user want to apply for a job:
- First, upload the resume by just calling `upload_resume` tool.
- If the upload is successful, use the response to fill in the required fields for `apply_for_job` payload.
- If the API response is missing some required fields, ask the candidate step by step for those specific fields.
- Once all required details are available, apply for the job using `apply_for_job`.

Note:
- Ask from user `apply_for_job` payload required fields if fields are empty.
"""

agent = Agent(
    "openai:gpt-4o-mini", mcp_servers=mcp_servers, system_prompt=system_prompt
)


async def main():
    async with agent:
        message_history = []
        while True:
            query = input("\nAsk me about cogent jobs! (or type 'q' to exit): ")
            if query.lower() == "q":
                break

            result = await agent.run(query, message_history=message_history)
            print("\n", result.output)

            message_history.extend(result.new_messages())
            if len(message_history) > 12:
                message_history.pop(0)


if __name__ == "__main__":
    asyncio.run(main())
