from PIL import Image, ExifTags

def get_coordinates(metadata):
    latitude_ref = metadata['GPSInfo'][1]
    latitude = metadata['GPSInfo'][2]
    longitude_ref = metadata['GPSInfo'][3]
    longitude = metadata['GPSInfo'][4]

    latitude_degrees = float(latitude[0])
    latitude_minutes = float(latitude[1])
    latitude_seconds = float(latitude[2])

    longitude_degrees = float(longitude[0])
    longitude_minutes = float(longitude[1])
    longitude_seconds = float(longitude[2])

    # Convert latitude values to decimal degrees
    latitude_decimal = latitude_degrees + latitude_minutes / 60 + latitude_seconds / 3600
    if latitude_ref == 'S':
        latitude_decimal *= -1

    # Convert longitude values to decimal degrees
    longitude_decimal = longitude_degrees + longitude_minutes / 60 + longitude_seconds / 3600
    if longitude_ref == 'W':
        longitude_decimal *= -1

    return latitude_decimal, longitude_decimal


def get_image_metadata(image_path):
    with Image.open(image_path) as img:
        metadata = img._getexif()

    if metadata is None:
        return {}  # No metadata found

    decoded_metadata = {}
    for tag, value in metadata.items():
        if tag in ExifTags.TAGS:
            tag_name = ExifTags.TAGS[tag]
            decoded_metadata[tag_name] = value

    return decoded_metadata
