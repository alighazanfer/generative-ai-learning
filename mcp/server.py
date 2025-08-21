import re
import httpx
import logging
import requests
from typing import List, Union
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

class JobDetail(Job):
    description: str = Field(description="Brief description of the job")
    organization_name: str = Field(description="Name of the organization offering the job")

class WorkExperience(BaseModel):
    requirement: int
    employer: str
    title: str
    start: str
    end: str

class Education(BaseModel):
    requirement: int
    school: str
    major: str
    start: str
    end: str

class Skill(BaseModel):
    id: int = Field(description="ID of the skill")
    title: str = Field(description="Title of the skill")

class Candidate(BaseModel):
    first_name: str = Field(description="Candidate first name")
    last_name: str = Field(description="Candidate last name")
    email: str = Field(description="Candidate email")
    phone: str = Field(description="Candidate phone number")
    address: str = Field(description="Candidate address")
    city: str = Field(description="Candidate city")
    gender: str = Field(description="Candidate gender")
    linkedin: str = Field(description="Candidate LinkedIn profile link")
    skills: List[Skill] = Field(description="List of skills of the candidate")

class ApplyForJob(BaseModel):
    candidate: Candidate
    job: int = Field(description="Get job id of the user requested job from the history and put it here")
    cv: str = Field(description="URL of uploaded resume")
    requirement_values: Union[WorkExperience, Education] = Field(description="List of work experiences and education details")
    source_type: str = "socialmedia"
    source_value: str = ""

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

    Returns:
        List[Job]: List of job summaries if successful.
        ErrorResponse: Error details if the request fails.
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
    Fetch detailed information about a published job if required.

    Args:
        uuid (str): UUID of the job to fetch.

    Returns:
        JobDetail: Detailed job info if successful.
        ErrorResponse: Error details if the request fails.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/jobs/{uuid}/view-job/")
            data = response.json()
            return JobDetail(**data)
    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}")    


@mcp.tool()
async def upload_resume() -> dict | ErrorResponse:
    """
    when user ask to apply for a job, call this tool to upload a local resume to the Hirestream.

    Returns:
        dict: API response after uploading the resume.
        ErrorResponse: Error details if download or upload fails.
    """

    try:
        resume_path = "testing_resume.pdf"
        with open(resume_path, "rb") as f:
            data = {"type": "cv"}
            files = {
                "file": (resume_path, f, "application/pdf")
            }
            response = requests.post(f"{BASE_URL}/workflows/upload/", data=data, files=files)
            data = response.json()
            return data

    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}")


@mcp.tool()
async def apply_for_job(payload: ApplyForJob, uuid: str) -> None | ErrorResponse:
    """
    Apply for a job on Hirestream using candidate and job details.

    Args:
        payload (ApplyForJob): Pydantic model containing all application data.
        uuid (str): UUID of the job to apply for.

    Returns:
        None: If the application succeeds.
        ErrorResponse: Error details if the request fails.
    """

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/jobs/{uuid}/view-job-requirements/")
            if response.status_code != 200:
                return ErrorResponse(error=f"Failed to apply for a job: {response.text}")
            data = response.json()
            
            logger.info(f"payload: {payload}")
            logger.info(f"Requirements: {data}")

            requirements = response.json().get("requirements", [])
            final_requirements = []
            for req in requirements:
                if req["type"] == "employment":
                    work_exps = [r.dict() for r in payload.requirement_values if isinstance(r, WorkExperience)]
                    for w in work_exps:
                        w["requirement"] = req["id"]
                        final_requirements.append(w)

                elif req["type"] == "education":
                    educations = [r.dict() for r in payload.requirement_values if isinstance(r, Education)]
                    for e in educations:
                        e["requirement"] = req["id"]
                        final_requirements.append(e)

            application_payload = payload
            logger.info(f"Final application payload: {application_payload}")
            application_payload["requirement_values"] = final_requirements

            response = await client.post(f"{BASE_URL}/workflows/job-applications/", json=application_payload)
            if response.status_code != 200:
                return ErrorResponse(error=f"Failed to apply for a job: {response.text}")
            
            return None
    except Exception as e:
        return ErrorResponse(error=f"Unexpected error: {str(e)}") 


if __name__ == '__main__':
    mcp.run(transport='stdio')
