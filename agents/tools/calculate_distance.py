from pydantic import BaseModel, Field
from langchain_core.tools import tool
class CalculateDistance(BaseModel):
    """Calculate the distance of location"""
    location: str = Field(..., description="The location to calculate the distance for")

@tool("distance_location_tool" , args_schema=CalculateDistance)
def calculate_distance_value(location: str) -> int:
    if location == "Aquarium":
        return 7800
    elif location == "Super Mall":
        return 11000
    else:
        return 0