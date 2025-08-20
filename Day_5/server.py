import httpx
from typing import List
from mcp.server.fastmcp import FastMCP
from models import JobSummary, JobDetail


mcp = FastMCP("MCP Server")
BASE_URL = "https://cogent-labs.hirestream.io/api/v1/jobs"


@mcp.tool()
def list_jobs() -> List[JobSummary]:
    """
    Fetch all published jobs from Hirestream API.
    Returns a list of JobSummary objects.
    """

    resp = httpx.get(f"{BASE_URL}/published-jobs")
    resp.raise_for_status()
    data = resp.json()

    jobs = [
        JobSummary(
            id=job["id"],
            title=job["title"],
            department=job["department"],
            location=job["location"],
        )
        for job in data.get("results", [])
    ]
    return jobs


@mcp.tool()
def view_job(job_id: int) -> JobDetail:
    """
    Get details for a specific job by job_id.
    Returns a JobDetail object.
    """

    resp = httpx.get(f"{BASE_URL}/{job_id}/view-job")
    resp.raise_for_status()
    data = resp.json()

    return JobDetail(
        id=data["id"],
        title=data["title"],
        department=data["department"]["title"],
        location=data["location"],
        organization=data["organization_name"],
        description=data["description"],
    )


if __name__ == "__main__":
    mcp.run()
