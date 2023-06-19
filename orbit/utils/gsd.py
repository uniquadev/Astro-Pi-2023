"""
GROUND SAMPLING DISTANCE
"""


def gsd(sensor_width, sensor_height, focal_length, flight_height):
    distance_width = (sensor_width * flight_height) / focal_length
    distance_height = (sensor_height * flight_height) / focal_length
    
    return distance_width, distance_height
