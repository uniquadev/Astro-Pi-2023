"""
PYTHON MODULE FOR IMAGE PROCESSING AND NDVI CALCULATIONS
"""

import cv2
import numpy as np

def ndvi(image) -> np.ndarray:
    """Calculate NDVI on the given image.

    Return a numpy ndarray with a NDVI value for each pixel of the image.
    """

    blue, green, red = cv2.split(image)
    
    bottom = (red.astype(float) + blue.astype(float))
    bottom[bottom==0] = 0.01  # Avoid zero division error
    ndvi = (blue.astype(float) - red) / bottom
    
    return ndvi

def mean_ndvi(image, remove_negatives=False) -> float:
    """ Calculate the mean NDVI value over all the pixels of the given image.

    Return a float representing the mean NDVI value of the image.
    """

    ndvi_array = ndvi(image)
    
    if remove_negatives:
        ndvi_array = [ndvi_array[i][j] for i in range(ndvi_array.shape[0]) for j in range(ndvi_array.shape[1]) if ndvi_array[i,j] >= 0]
    mean_ndvi = np.mean(ndvi_array)

    return mean_ndvi
