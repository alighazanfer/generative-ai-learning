import re
import httpx
from typing import List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP


mcp = FastMCP("Apply-for-a-job")
BASE_URL = "https://cogent-labs.hirestream.io/api/v1"
 

class Job(BaseModel):
    uuid: str = Field(description="Unique identifier for the job")
    title: str = Field(description="Title of the job")
    department: str = Field(description="Department name of the job")
    location: str = Field(description="Location of the job")
    # positions: int = Field(description="Number of positions available for the job")

class JobDetail(Job):
    description: str = Field(description="Brief description of the job")
    organization_name: str = Field(description="Name of the organization offering the job")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


@mcp.tool()
async def get_published_jobs() -> List[Job] | ErrorResponse:
    """
    Fetch all published jobs from Hirestream API.
    Returns a list of job objects or an error response.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/jobs/published-jobs/")
            data = response.json()
            results = data.get("results", [])
            jobs = [Job(**job) for job in results]
            return jobs
    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}")


@mcp.tool()
async def get_published_job_detail(uuid: str) -> Job | ErrorResponse:
    """
    Fetch published job details from the Hirestream API.

    Args:
        uuid: The UUID of the published job to fetch.

    Returns the The published job detail
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/jobs/{uuid}/view-job/")
            data = response.json()
            return JobDetail(**data)
    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}")


@mcp.tool()
async def download_and_upload_resume(google_drive_url: str) -> dict | ErrorResponse:
    """
    When user asked to apply for a job, this tool will:
    1. Download a resume from a Google Drive link.
    2. Upload it to the Hirestream API.
    3. Return the upload response.

    Args:
        google_drive_url: The full Google Drive share link.
    """

    try:
        match = re.search(r"/d/([^/]+)/", google_drive_url)
        if not match:
                return ErrorResponse(error="Invalid Google Drive URL.")
        
        download_url = f"https://drive.google.com/uc?export=download&id={google_drive_url.split('/').pop()}"

        async with httpx.AsyncClient() as client:
            drive_response = await client.get(download_url)
            if drive_response.status_code != 200:
                return ErrorResponse(error=f"Failed to download file: {drive_response.text}")

            files = {"file": ("resume.pdf", drive_response.content, "application/pdf")}
            upload_response = await client.post(f"{BASE_URL}/workflows/upload/", files=files)
            if upload_response.status_code != 200:
                return ErrorResponse(error=f"Failed to upload resume: {upload_response.text}")

            upload_data = upload_response.json()
            return upload_data

    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    mcp.run(transport='stdio')
