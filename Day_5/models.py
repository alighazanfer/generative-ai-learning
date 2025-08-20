from pydantic import BaseModel


class JobSummary(BaseModel):
    id: int
    title: str
    department: str
    location: str


class JobDetail(BaseModel):
    id: int
    title: str
    department: str
    location: str
    organization: str
    description: str
