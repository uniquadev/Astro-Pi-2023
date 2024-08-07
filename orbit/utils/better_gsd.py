from math import radians, sin, cos, sqrt, asin

def better_gsd(horizontal_aov, vertical_aov, flight_height):
    horizontal_aov = radians(horizontal_aov)
    vertical_aov = radians(vertical_aov)

    earth_radius = 6371 * 10**3  # meters

    b = -2 * (earth_radius + flight_height) * cos(vertical_aov / 2)
    c = (earth_radius + flight_height) ** 2 - earth_radius ** 2
    x = (-b - sqrt(b**2 - 4*c)) / 2

    
    delta_lat = 2 * asin( (x * sin(vertical_aov / 2)) / earth_radius )
    

    b = -2 * (earth_radius + flight_height) * cos(horizontal_aov / 2)
    x = (-b - sqrt(b**2 - 4*c)) / 2

    
    delta_lon = 2 * asin( (x * sin(horizontal_aov / 2)) / earth_radius )

    distance_width = delta_lon * earth_radius
    distance_height = delta_lat * earth_radius

    return distance_width, distance_height
