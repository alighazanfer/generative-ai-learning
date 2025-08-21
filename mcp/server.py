import re
import httpx
import logging
from typing import List
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlparse, parse_qs


mcp = FastMCP("Cogentlabs-Hirestream")
BASE_URL = "https://cogent-labs.hirestream.io/api/v1"
 
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class Job(BaseModel):
    id: int = Field(description="ID of the job")
    uuid: str = Field(description="UUID of the job")
    title: str = Field(description="Title of the job")
    department: str = Field(description="Department name of the job")
    location: str = Field(description="Location of the job")
    # positions: int = Field(description="Number of positions available for the job")

class JobDetail(Job):
    description: str = Field(description="Brief description of the job")
    organization_name: str = Field(description="Name of the organization offering the job")

class ErrorResponse(BaseModel):
    error: str = Field(description="Error message")


def extract_drive_id(url: str) -> str | None:
    """
    Extract the file ID from various Google Drive URL formats.
    Returns None if no ID found.
    """

    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "id" in qs:
        return qs["id"][0]

    match = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)

    return None


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
async def download_and_upload_resume(google_drive_url: str, job_id: int) -> None | ErrorResponse:
    """
    When user asked to apply for a job, this tool will:
    1. Download a resume from a Google Drive link.
    2. Upload it to the Hirestream API.

    Args:
        google_drive_url: The full Google Drive share link.
        job_id: Get the ID of the user requested job from the get_published_job_detail, if not available in the history.
    """

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            # Step 1: Download the resume from Google Drive
            file_id = extract_drive_id(google_drive_url)
            drive_response = await client.get(f"https://drive.google.com/uc?export=download&id={file_id}")
            if drive_response.status_code != 200:
                return ErrorResponse(error=f"Failed to download file: {drive_response.text}")

            #Step 2: Upload the resume to the Hirestream API
            uploaded_resume = {
                "file": "resume.pdf",
                "content_type": "application/pdf",
                "file_content": drive_response.content
            }

            upload_response = await client.post(f"{BASE_URL}/workflows/upload/", files=uploaded_resume)
            if upload_response.status_code != 200:
                return ErrorResponse(error=f"Failed to upload resume: {upload_response.text}")
            
            upload_data = upload_response.json()
            logger.info(f"Resume uploaded for job {job_id} successfully: {upload_data}")

            #Step 3: Apply for the job application to the Hirestream API
            apply_job_payload = {
                "job": job_id,
                "cv": upload_data.get("url"),
                "candidate": {
                    "gender": "male",
                    "first_name": upload_data.get("first_name", "john"),
                    "last_name": upload_data.get("last_name", "doe"),
                    "email": upload_data.get("email", "johndoe@gmail.com"),
                    "phone": upload_data.get("phone"),
                    "address": upload_data.get("address"),
                    "city": upload_data.get("city"),
                    "skills": upload_data.get("skills", []),
                },
                "requirement_values": (
                    upload_data.get("requirement_values", [])
                    + [
                        {"requirement": 800, "value": "34324"}, 
                        {"requirement": 797, "value": "234234"},
                        {"requirement": 798, "value": "2"}, 
                        {"requirement": 799, "value": "2"},
                    ]
                ),
                "source_type": "socialmedia",
                "source_value": "",
            }

            apply_job_response = await client.post(f"{BASE_URL}/workflows/job-applications/", json=apply_job_payload)
            if apply_job_response.status_code != 200:
                return ErrorResponse(error=f"Failed to apply for a job: {apply_job_response.text}")
            
            return None

    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}")


if __name__ == '__main__':
    mcp.run(transport='stdio')
