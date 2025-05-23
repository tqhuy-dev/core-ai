from pydantic import BaseModel, Field
from langchain_core.tools import tool
class CalculateFlightValue(BaseModel):
    """Calculate the value of a flight based on location and brand"""
    flight_location: str = Field(..., description="The location of the flight to calculate the value for")
    flight_brand: str = Field(..., description="The brand of the flight to calculate the value for")

@tool("flight_value_tool" , args_schema=CalculateFlightValue)
def calculate_flight_value(flight_location: str,flight_brand: str) -> int:
    print(f"flight_location: {flight_location} flight_brand: {flight_brand}")
    bonus_fee = 0
    if flight_brand == "France":
        bonus_fee = 1000
    if flight_location == "London":
        return 1000 + bonus_fee
    elif flight_location == "Paris":
        return 2000 + bonus_fee
    elif flight_location == "Berlin":
        return 3000 + bonus_fee
    else:
        return 500 + bonus_fee



def CommonTool(map_flight: dict):
    @tool("flight_value_tool", args_schema=CalculateFlightValue)
    def calculate_flight_value_v2(flight_location: str) -> int:
        if flight_location in map_flight:
            return map_flight[flight_location]
        else:
            return 0
    return calculate_flight_value_v2