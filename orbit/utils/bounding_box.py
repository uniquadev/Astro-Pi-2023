from math import radians, degrees, cos, sin, atan2

def calculate_bounding_box_coordinates(iss_latitude, iss_longitude, width, height):
    # Convert latitude and longitude to radians
    lat_rad = radians(iss_latitude)
    lon_rad = radians(iss_longitude)

    # Earth radius in meters
    earth_radius = 6371 * 10**3

    # Convert ISS coordinates to Cartesian coordinates
    x = earth_radius * cos(lat_rad) * cos(lon_rad)
    y = earth_radius * cos(lat_rad) * sin(lon_rad)

    # Calculate half the width and half the height
    half_width = width / 2
    half_height = height / 2

    # Calculate the four corners of the bounding box
    top_left_x = x - half_width
    top_left_y = y + half_height

    top_right_x = x + half_width
    top_right_y = y + half_height

    bottom_left_x = x - half_width
    bottom_left_y = y - half_height

    bottom_right_x = x + half_width
    bottom_right_y = y - half_height

    # Convert Cartesian coordinates back to latitude and longitude
    top_left_lat = degrees(atan2(top_left_y, cos(lat_rad) * cos(lon_rad)))
    top_left_lon = degrees(atan2(top_left_x, cos(lat_rad) * sin(lon_rad)))

    top_right_lat = degrees(atan2(top_right_y, cos(lat_rad) * cos(lon_rad)))
    top_right_lon = degrees(atan2(top_right_x, cos(lat_rad) * sin(lon_rad)))

    bottom_left_lat = degrees(atan2(bottom_left_y, cos(lat_rad) * cos(lon_rad)))
    bottom_left_lon = degrees(atan2(bottom_left_x, cos(lat_rad) * sin(lon_rad)))

    bottom_right_lat = degrees(atan2(bottom_right_y, cos(lat_rad) * cos(lon_rad)))
    bottom_right_lon = degrees(atan2(bottom_right_x, cos(lat_rad) * sin(lon_rad)))

    return [(top_left_lat, top_left_lon), (top_right_lat, top_right_lon),
            (bottom_left_lat, bottom_left_lon), (bottom_right_lat, bottom_right_lon)]
