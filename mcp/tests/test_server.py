import json
import pytest
from pydantic_ai import Agent
from dotenv import load_dotenv
from inline_snapshot import snapshot
from mock_data import mock_resume_data
from pydantic_ai.mcp import MCPServerStdio

load_dotenv()


@pytest.fixture
def test_agent():
    """Fixture to provide the AI agent with MCP server integration."""

    agent = Agent(
        "openai:gpt-4o-mini",
        toolsets=[MCPServerStdio("python", ["server.py"])],
        system_prompt="""
            You are a helpful assistant for job seekers. 
            Always fetch jobs and allow user to apply through Hirestream api.
        """,
    )

    return agent


# --------------------------------------------------------------------
# Helper Functions
# --------------------------------------------------------------------
def _extract_tool_calls(result):
    """Extract tool calls from agent result history."""

    tool_calls = []
    history = result.new_messages()

    for message in history:
        try:
            for part in message.parts:
                if hasattr(part, "part_kind") and part.part_kind == "tool-call":
                    tool_calls.append(
                        {
                            "tool_name": part.tool_name,
                            "args": json.loads(part.args)
                            if isinstance(part.args, str)
                            else part.args,
                        }
                    )
        except Exception as e:
            print(f"Error parsing history: {e}")

    return tool_calls


def _find_tool_call(tool_calls, tool_name):
    """Find a specific tool call by name."""
    for call in tool_calls:
        if call["tool_name"] == tool_name:
            return call
    return None


# --------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------
class TestGetPublishedJobs:
    """Unit test to verify exact tool call format."""

    @pytest.mark.asyncio
    async def test_tool_call(self, test_agent):
        """Test exact format of tool call."""

        async with test_agent:
            result = await test_agent.run("Get all published jobs")

        tool_calls = _extract_tool_calls(result)
        jobs_call = _find_tool_call(tool_calls, "get_published_jobs")

        assert jobs_call == snapshot({"tool_name": "get_published_jobs", "args": {}})


class TestApplyToJob:
    """Unit test to verify exact tool call format."""

    @pytest.mark.asyncio
    async def test_apply_to_job(self, test_agent):
        """Test apply to job."""

        resume_data = await mock_resume_data()
        user_prompt = (
            "Apply to job of Generative AI Engineer. I am male and my linkedin is https://www.linkedin.com/in/alicejohnson"
            + str(resume_data)
        )

        async with test_agent:
            result = await test_agent.run(user_prompt)

        tool_calls = _extract_tool_calls(result)
        jobs_call = _find_tool_call(tool_calls, "apply_for_job")

        candidate_email = jobs_call["args"]["payload"]["candidate"]["email"]
        assert candidate_email == snapshot("alice.johnson@example.com")
