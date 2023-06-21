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
def show_img(image: np.array, title: str):
    """Show an image.
    
    Args:
        image (np.array): the image to be displayed.
        title (str): the title of the window showing the image.

    """
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize_img(image: str, scale_factor: float):
    """Resize an image.

    Args:
        image (np.array): the image to be resized.
        scale_factor (float): the scale factor used to resize the image.
    
    Returns:
        np.array: The resized image.

    """
    resized = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
    return resized


def load_images(folder: str):
    """Load images from a given folder.
    Args:
        folder (str): the path to the folder.

    Returns:
        list: A list with a path for each image in the given folder.
    """
    images_path = []
    images = os.listdir(folder)

    for image in images:
        images_path.append(folder + image)

    return images_path


# --------------------------------------
# CLASSIFIERS
# --------------------------------------
class BaseClassifier:
    """The base class for a classifier
    
    Attributes:
        images_path (Path): The path to the folder containing the images to be filtered.
        out_dir (Path): The output folder that will contain the images filtered.
    """

    def __init__(self, images_path: Path, out_dir: Path) -> None:
        """ Instantiate the classifier.

        Args:
            images_path (Path): The path to the folder containing the images to be filtered.
            out_dir (Path): The output folder that will contain the images filtered.

        """
        self.images_path = images_path
        self.out_dir = out_dir

    def start(self):
        pass


""" A water classifier to use with a google earth engine script

class WaterClassifier(BaseClassifier):
    def start(self, water_threshold):

        with open('./water_percentages.json') as json_file:
            data = json.load(json_file)

            for feature in data["features"]:
                path = self.images_path / feature["properties"]["path"].split("/")[-1]
                water_percentage = feature["properties"]["water_percentage"]

                if water_percentage < water_threshold:
                    copy_file(path, self.out_dir)
"""


class DarkImageClassifier(BaseClassifier):
    """Classifier to remove dark images.
    """

    def start(self, threshold):
        """Analyze the images in self.images_path by turning the images into grayscale and 
        calculating the average intensity of the pixels. Then it moves the non-dark images into self.out_dir.

        Args:
            threshold: The maximum average intensity to keep an image.

        """
        for path in self.images_path.iterdir():
            image = cv2.imread(str(path))
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            avg_intensity = np.average(gray)

            if avg_intensity > threshold:
                copy_file(path, self.out_dir)



class OtsuThresholdClassifier(BaseClassifier):
    """Classifier to remove images taken over clouds using the otsu method.
    """

    def start(self, percentage_threshold):
        """Analyze the images in self.images_path by applying the otsu method which is 
        calculating and applying the optimal threshold in order to distinguish the foreground (clouds) from the background for each image.
        After applying the threshold it calculates the percentage of the image covered by clouds and 
        moves the images with a percentage lower than percentage_threshold into self.out_dir.


        Args:
            percentage_threshold: The maximum percentage of clouds to keep an image.

        """
        for path in self.images_path.iterdir():
            image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            pixel_count = cv2.countNonZero(thresholded)
            total_pixels = thresholded.size

            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                copy_file(path, self.out_dir)



class ThresholdClassifier(BaseClassifier):
    """A simple threshold classifier to remove images taken over clouds.
    """

    def start(self, pixel_threshold, percentage_threshold):
        """Analyze the images in self.images_path by selecting the green channel and applying a pixel_threshold 
        in order to distinguish between cloud pixels and non-cloud pixels.
        It then calculates the percentage of cloud pixels for each image in order to decide whether to discard or 
        copy the image into self.out_dir.

        Args:
            pixel_threshold: The threshold to apply to each pixel of each image.
            percentage_threshold: The maximum percentage of clouds to keep an image.

        """
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
    """A classifier to remove images taken over water that makes use of the ndvi in order to distinguish water pixels"""

    def start(self, ndvi_range, percentage_threshold):
        """Analyze the images in self.images_path by calculating the ndvi over each image and 
        classifying water pixels using the ndvi range provided. Then it calculates the percentage of water pixels for each image 
        to decide whether to discard it or copy it in self.out_dir.

        Args:
            ndvi_range: The ndvi range to distinguish water pixels.
            percentage_threshold: The maximum percentage of water to keep an image.

        """
        for path in self.images_path.iterdir():
            image = cv2.imread(str(path), cv2.IMREAD_COLOR)
            image_pixels = np.array(image, dtype=float) / float(255)

            total_pixels = image_pixels.size
            ndvi_values = ndvi(image_pixels)
            pixel_count = np.count_nonzero((ndvi_values < ndvi_range[1]) & (ndvi_values > ndvi_range[0]))

            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                copy_file(path, self.out_dir)
