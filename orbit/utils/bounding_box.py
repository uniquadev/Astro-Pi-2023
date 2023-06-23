import sys
import csv
import shutil
from logzero import logger
from datetime import datetime
from pathlib import Path
from math import radians, degrees

from gsd import gsd
from better_gsd import better_gsd
from iss import iss_altitude
from metadata import get_image_metadata, get_coordinates


SENSOR_WIDTH = 6.2928  # mm
SENSOR_HEIGHT = 4.712  # mm
FOCAL_LENGTH = 4.735  # mm
IMAGE_WIDTH = 4056  # pixels
IMAGE_HEIGHT = 3040  # pixels
HORIZONTAL_AOV = 72.64  # degrees
VERTICAL_AOV = 57.12  # degrees

def adjust_latitude_longitude(latitude, longitude):
    adjusted_latitude = latitude if latitude <= 90 else latitude - 180
    adjusted_longitude = longitude if longitude <= 180 else longitude - 360
    
    return adjusted_latitude, adjusted_longitude

def bounding_box(iss_latitude, iss_longitude, width, height):
    # Convert latitude and longitude to radians
    lat_rad = radians(iss_latitude)
    lon_rad = radians(iss_longitude)

    # Earth radius in meters
    earth_radius = 6371 * 10**3

    # Calculate half the width and half the height
    half_width = width / 2
    half_height = height / 2

    # Calculate the four corners of the bounding box
    lat_delta = half_height / earth_radius
    lon_delta = half_width / earth_radius

    top_left = (degrees(lat_rad + lat_delta), degrees(lon_rad - lon_delta))
    top_right = (degrees(lat_rad + lat_delta), degrees(lon_rad + lon_delta))
    bottom_left = (degrees(lat_rad - lat_delta), degrees(lon_rad - lon_delta))
    bottom_right = (degrees(lat_rad - lat_delta), degrees(lon_rad + lon_delta))

    top_left = adjust_latitude_longitude(top_left[0], top_left[1])
    top_right = adjust_latitude_longitude(top_right[0], top_right[1])
    bottom_left = adjust_latitude_longitude(bottom_left[0], bottom_left[1])
    bottom_right = adjust_latitude_longitude(bottom_right[0], bottom_right[1])


    if top_left[1] > top_right[1]:
        top_left, top_right = top_right, top_left

    if bottom_left[1] > bottom_right[1]:
        bottom_left, bottom_right = bottom_right, bottom_left

    if top_left[0] < bottom_left[0]:
        top_left, bottom_left = bottom_left, top_left

    if top_right[0] < bottom_right[0]:
        top_right, bottom_right = bottom_right, top_right

    return top_left, top_right, bottom_left, bottom_right



class BoundingBoxMaker:

    def __init__(self, images_path : Path, out_dir : Path) -> None:
        self.images_path = images_path
        self.out_dir = out_dir

        self.fieldnames = ["path", "xmin", "ymin", "xmax", "ymax"]


        self.out_dir.mkdir(parents=True, exist_ok=True)
        with open(self.out_dir / "bounding_boxes.csv", "a+") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()

    def start(self, sensor_width, sensor_height, focal_length):
        for path in self.images_path.iterdir():
            metadata = get_image_metadata(path)
            date = datetime.strptime(str(metadata["DateTimeOriginal"]), "%Y:%m:%d %H:%M:%S")
            timestamp = datetime.timestamp(date)
            flight_height = iss_altitude(timestamp)
            distance_width, distance_height = better_gsd(HORIZONTAL_AOV, VERTICAL_AOV, flight_height)
            latitude, longitude = get_coordinates(metadata)
            top_left, top_right, bottom_left, bottom_right = bounding_box(latitude, longitude, distance_width, distance_height)

            data = [path, bottom_left[1], bottom_left[0], top_right[1], top_right[0]]

            with open(self.out_dir / "bounding_boxes.csv", 'a') as f:
                writer = csv.writer(f)

                # write the data
                writer.writerow(data)


def main(argc, argv):

    # Check command-line arguments
    if argc != 2:
        sys.exit(1)
    
    # Get the path to the folder containing the images
    path = Path(argv[1])

    # Check if the path exists
    if not path.exists():
        sys.exit(1)

    box_maker = BoundingBoxMaker(path, out_folder)
    box_maker.start(SENSOR_WIDTH, SENSOR_HEIGHT, FOCAL_LENGTH)

    print("Finished")

if __name__ == "__main__":
    # Resolve absolute path to the current code directory
    base_folder: Path = Path(__file__).parent.resolve()
    # Define output folder for images
    out_folder = base_folder / "boxes"

    shutil.rmtree(out_folder, ignore_errors=True)

    # Set log file
    main(len(sys.argv), sys.argv)
