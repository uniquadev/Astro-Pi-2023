# --------------------------------------
# IMPORTS
# --------------------------------------
import os # Operating system dependent functionality
import cv2 # Image processing
import json
from datetime import datetime
from shutil import copy as copy_file # Move files
from pathlib import Path  # Path utilities
import numpy as np # Array manipulation
from global_land_mask import globe # reverse geocoding for water
from PIL import Image
from PIL.ExifTags import TAGS

from .ndvi import ndvi # Normalized Difference Vegetation Index
from .gsd import gsd
from .iss import iss_altitude
from .bounding_box import bounding_box
from utils.metadata import get_image_metadata, get_coordinates


# --------------------------------------
# FUNCTIONS
# --------------------------------------
def show_img(image : str, title : str):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize_img(image : str, scale_factor : float):
    resized = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
    return resized


def load_images(folder : str):
    images_path = []
    images = os.listdir(folder)

    for image in images:
        images_path.append(folder + image)

    return images_path

# --------------------------------------
# CLASSIFIERS
# --------------------------------------
class BaseClassifier:

    def __init__(self, images_path : Path, out_dir : Path) -> None:
        self.images_path = images_path
        self.out_dir = out_dir

    def start(self):
        pass


class WaterClassifier(BaseClassifier):

    def start(self, water_threshold):

        with open('./water_percentages.json') as json_file:
            data = json.load(json_file)

            for feature in data["features"]:
                path = self.images_path / feature["properties"]["path"].split("/")[-1]
                water_percentage = feature["properties"]["water_percentage"]

                if water_percentage < water_threshold:
                    copy_file(path, self.out_dir)



class DarkImageClassifier(BaseClassifier):

    def start(self, threshold):
        for path in self.images_path.iterdir():
            image = cv2.imread(str(path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            avg_intensity = np.average(gray)

            if avg_intensity > threshold:
                copy_file(path, self.out_dir)



class OtsuThresholdClassifier(BaseClassifier):

    def start(self, percentage_threshold):
        for path in self.images_path.iterdir():
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            pixel_count = cv2.countNonZero(thresholded)
            total_pixels = thresholded.size

            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                copy_file(path, self.out_dir)



class ThresholdClassifier(BaseClassifier):

    def start(self, pixel_threshold, percentage_threshold):
        for path in self.images_path.iterdir():
            nir_image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            nir_channel = nir_image[:, :, 1]  # Select the green challenge of each pixel

            _, mask = cv2.threshold(nir_channel, int(pixel_threshold * 255), 255, cv2.THRESH_BINARY)

            red_mask = np.zeros_like(nir_image)  # Array with same size of nir_image filled with 0s
            red_mask[:, :, 2] = mask  # Set the red channel of the mask to the cloud mask

            total_pixels = mask.size

            # Count the number of cloud pixels
            pixel_count = np.count_nonzero(mask)

            # Calculate the percentage of cloud pixels
            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                copy_file(path, self.out_dir)


class NDVIClassifier(BaseClassifier):

    def start(self, ndvi_range, percentage_threshold):
        for path in self.images_path.iterdir():
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            image_pixels = np.array(image, dtype=float) / float(255)

            total_pixels = image_pixels.size
            ndvi_values = ndvi(image_pixels)
            pixel_count = np.count_nonzero((ndvi_values < ndvi_range[1]) & (ndvi_values > ndvi_range[0]))

            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                copy_file(path, self.out_dir)
