import json
import httpx
import logging
import traceback
from typing import List, Any
from models import JobSummary


class APIClient:
    def __init__(
        self,
        base_api_url: str = "https://cogent-labs.hirestream.io/api/v1/jobs",
        logger=None,
    ):
        self.base_api_url = base_api_url
        if logger is None:
            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.INFO)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)
        else:
            self.logger = logger

    async def _api_call(self, method: str, endpoint: str, payload: dict | None = None) -> dict:
        """Utility function for API calls to Hirestream."""

        url = f"{self.base_api_url}/{endpoint}"
        data = json.dumps(payload) if payload else None
        headers = {
            "Content-Type": "application/json",
        }

        if self.logger:
            self.logger.debug(
                f"Request: {method} {url} Headers: {headers} Payload: {data}"
            )

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(
                    method, url, headers=headers, data=data, follow_redirects=False
                )

            if self.logger:
                self.logger.debug(
                    f"Response status: {response.status_code} Response: {response.text}"
                )

            if response.status_code >= 400:
                if self.logger:
                    self.logger.error(
                        f"API Error {response.status_code}: {response.text}"
                    )
                raise Exception(f"API Error {response.status_code}: {response.text}")

            try:
                return response.json()
            except Exception:
                if self.logger:
                    self.logger.error(f"JSON Parsing: {response.text}")
                return {"text": response.text}

        except Exception as e:
            traceback.print_exc()
            if self.logger:
                self.logger.error(f"{e}")
            return {"text": str(e)}

    async def list_jobs(self) -> List[JobSummary] | Any:
        """Fetch all published jobs from Hirestream API."""
        data = await self._api_call("GET", "/published-jobs")

        if not data or "results" not in data:
            return []

        jobs = [
            JobSummary(
                id=job.get("id"),
                title=job.get("title"),
                department=job.get("department"),
                location=job.get("location"),
            )
            for job in data["results"]
        ]
        
        return jobs
