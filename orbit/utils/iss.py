"""
Some functions to get info about ISS
"""

import requests

def iss_altitude(timestamp) -> float:
    """The function to get the ISS altitude given a timestamp"""
    api_url = f"https://api.wheretheiss.at/v1/satellites/25544?timestamp={timestamp}"
    r = requests.get(api_url).json()
    
    return r["altitude"]
