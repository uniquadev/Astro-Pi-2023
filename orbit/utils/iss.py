"""
Some functions to get info about ISS
"""

import sys
import requests

def iss_altitude(timestamp) -> float:
    """The function to get the ISS altitude given a timestamp"""
    api_url = f"https://api.wheretheiss.at/v1/satellites/25544?timestamp={timestamp}"
    r = requests.get(api_url).json()
    
    return r["altitude"] * 10**3


def main(argc : int, argv : list[str]):
    # check arguments
    if argc != 2:
        print("Usage: python3 iss.py <timestamp>")
        return

    print(f'Altitude: {iss_altitude(float(argv[1]))}')


if __name__ == '__main__':
    main(len(sys.argv), sys.argv)
