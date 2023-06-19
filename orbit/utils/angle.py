import re

def degrees_to_decimal(metadata):
    # Calculate the sign based on the direction (N, S, E, W)
    if 'N' or 'E' in metadata:
        sign = 1
    elif 'S' or 'W' in metadata:
        sign = -1
    else:
        raise ValueError("Invalid metadata direction. Valid directions are N, S, E, W.")

    pattern = r'(\d+)°\s*(\d+)\'\s*(\d+(?:\.\d+)?)\"'

    # Search for matches in the metadata using the regex pattern
    matches = re.search(pattern, metadata)

    if matches:
        degrees = int(matches.group(1))
        minutes = int(matches.group(2))
        seconds = float(matches.group(3))
    else:
        raise ValueError("Unable to parse metadata.")
    
    # Ensure positive values for calculations
    degrees = abs(degrees)
    minutes = abs(minutes)
    seconds = abs(seconds)
    
    # Convert degrees, minutes, and seconds to decimal degrees
    decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)
    
    # Apply the sign to the decimal degrees
    decimal_degrees *= sign
    
    return decimal_degrees
