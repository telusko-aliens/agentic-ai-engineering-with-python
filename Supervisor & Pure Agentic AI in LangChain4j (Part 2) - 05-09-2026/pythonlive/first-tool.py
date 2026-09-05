from langchain_core.tools import tool
from datetime import datetime
from zoneinfo import ZoneInfo

@tool
def current_time(city: str) -> str:
    """Get the current time in a city. Use it whenever the user asks about time."""
    zones = {
        "mumbai": "Asia/Kolkata",
        "delhi": "Asia/Kolkata",
        "london": "Europe/London",
        "new york": "America/New_York",
    }
    zone = zones.get(city.lower())
    if zone is None:
        return f"I do not know the timezone for {city}."
    return datetime.now(ZoneInfo(zone)).strftime("%d %B %Y, %I:%M %p")

@tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers and return the exact result."""
    return a * b

print(multiply.invoke({"a": 98765, "b": 43210}))



# print("name : ", current_time.name)
# print("description : ", current_time.description)
# print("args :", current_time.args)
# print()

# print(current_time.invoke({"city": "Mumbai"}))
