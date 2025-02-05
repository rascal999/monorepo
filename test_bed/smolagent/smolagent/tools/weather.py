import requests
from typing import Optional
from smolagents import tool

@tool
def get_weather(location: str, celsius: Optional[bool] = True) -> str:
    """
    Get the current weather at the given location using wttr.in.

    Args:
        location: The location (city name, airport code, etc.)
        celsius: Whether to return the temperature in Celsius (default is True)

    Returns:
        A string containing the current weather at the location.
    """
    try:
        # Format options:
        # ?format=%C:+%t+%h+%w+%m -> Condition: temp humidity wind moon_phase
        # ?format=%l:+%C+%t&m -> Location: condition temp (metric)
        # 0?q -> quiet output (no ASCII art)
        # &m -> metric units
        # &M -> wind speed in m/s
        
        units = "&m" if celsius else ""
        url = f"https://wttr.in/{location}?format=%l:+%C+%t+%h+%w{units}&M"
        
        response = requests.get(url, headers={'User-Agent': 'curl'}, timeout=10)
        response.raise_for_status()
        
        # Clean up the response
        weather = response.text.strip()
        
        # Get additional details
        details_url = f"https://wttr.in/{location}?format=+%m+%p{units}&M"
        details_response = requests.get(details_url, headers={'User-Agent': 'curl'}, timeout=10)
        details_response.raise_for_status()
        details = details_response.text.strip()
        
        return f"{weather}\n{details}"
        
    except requests.exceptions.RequestException as e:
        return f"Error fetching weather data: {str(e)}"