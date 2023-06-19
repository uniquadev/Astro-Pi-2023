import os
import cv2
import numpy as np
from pathlib import Path

from ndvi import ndvi


def show_img(image, title):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def resize_img(image, scale_factor):
    resized = cv2.resize(image, None, fx=scale_factor, fy=scale_factor)
    return resized


def load_images(folder):
    images_path = []
    images = os.listdir(folder)

    for image in images:
        images_path.append(folder + image)

    return images_path


class DarkImageClassifier:

    def __init__(self, images_path, out_dir) -> None:
        self.images_path = images_path
        self.out_dir = out_dir

    def start(self, threshold):
        for path in self.images_path:
            image = cv2.imread(path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            avg_intensity = np.average(gray)

            if avg_intensity > threshold:
                os.system(f"cp {path} {self.out_dir}")



class OtsuThresholdClassifier:

    def __init__(self, images_path, out_dir) -> None:
        self.images_path = images_path
        self.out_dir = out_dir

    def start(self, percentage_threshold):
        for path in self.images_path:
            image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            _, thresholded = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            pixel_count = cv2.countNonZero(thresholded)
            total_pixels = thresholded.size

            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                os.system(f"cp {path} {self.out_dir}")



class ThresholdClassifier:

    def __init__(self, images_path, out_dir) -> None:
        self.images_path = images_path
        self.out_dir = out_dir


    def start(self, pixel_threshold, percentage_threshold):
        for path in self.images_path:
            print(path)
            nir_image = cv2.imread(path, cv2.IMREAD_COLOR)
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
                os.system(f"cp {path} {self.out_dir}")


class NDVIClassifier:

    def __init__(self, images_path, out_dir) -> None:
        self.images_path = images_path
        self.out_dir = out_dir

    def start(self, ndvi_range, percentage_threshold):
        for path in self.images_path:
            image = cv2.imread(path, cv2.IMREAD_COLOR)
            image_pixels = np.array(image, dtype=float) / float(255)

            total_pixels = image_pixels.size
            ndvi_values = ndvi(image_pixels)
            pixel_count = np.count_nonzero((ndvi_values < ndvi_range[1] & ndvi_values > ndvi_range[0]))

            percentage = round((pixel_count / total_pixels) * 100, 1)

            if percentage < percentage_threshold:
                os.system(f"cp {path} {self.out_dir}")