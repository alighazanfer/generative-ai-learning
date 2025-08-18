from typing import List, Optional
from pydantic import BaseModel, Field


class RouterDecision(BaseModel):
    status: str = Field(description="Either 'PLANNING' or 'CASUAL'")
    answer: Optional[str] = Field(description="If status is 'CASUAL', include a natural reply. If 'PLANNING', set to None")


class DesignationSummary(BaseModel):
    package_duration: Optional[str] = Field(description="Duration of the package")
    price: Optional[str] = Field(description="Price of the package")
    meals: Optional[str] = Field(description="Meals information")
    highlights: Optional[List[str]] = Field(description="Array of highlights")


class DesignationInfo(BaseModel):
    found: bool = Field(description="Whether the designation was found in the context")
    name: Optional[str] = Field(description="Name of the designation")
    summary: DesignationSummary = Field(description="Summary of the package details")


class GlobalState(BaseModel):
    query: str
    casual_answer: Optional[str] = None
    designation_info: Optional[DesignationInfo] = None
    flight_info: Optional[str] = None
    weather_info: Optional[str] = None
    budget_info: Optional[str] = None
    itinerary: Optional[str] = None
