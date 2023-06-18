"""
PYTHON MODULE FOR IMAGE PROCESSING AND NDVI CALCULATIONS
"""

import cv2
import numpy as np

def ndvi(image_pixels) -> np.ndarray:
    """Calculate NDVI on the given image.

    Return a numpy ndarray with a NDVI value for each pixel of the image.
    """

    blue, green, red = cv2.split(image_pixels)
    
    bottom = (red.astype(float) + blue.astype(float))
    bottom[bottom==0] = 0.01  # Avoid zero division error
    ndvi = (blue.astype(float) - red) / bottom
    
    return ndvi

def mean_ndvi(image_pixels) -> float:
    """ Calculate the mean NDVI value over all the pixels of the given image.

    Return a float representing the mean NDVI value of the image.
    """

    ndvi_array = ndvi(image)
    mean_ndvi = np.mean(ndvi_array)

    return mean_ndvi
