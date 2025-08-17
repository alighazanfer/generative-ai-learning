from typing import TypedDict, List, Optional

class Summary(TypedDict, total=False):
    package_duration: str
    price: str
    hotel: str
    meals: str
    highlights: List[str]
    transport: str

class DesignationInfo(TypedDict, total=False):
    status: bool
    designation_name: str
    summary: Summary

class GlobalState(TypedDict):
    query: str
    casual_answer: str
    designation_info: DesignationInfo
    flight_info: str
    weather_info: str
    budget_info: Optional[dict]
    
