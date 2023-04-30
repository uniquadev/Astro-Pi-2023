"""
PYTHON MODULE FOR IMAGE PROCESSING AND NDVI CALCULATIONS
"""

import cv2
import numpy as np

class AstroImage:
    """A class to facilitate analysis with images taken from ISS.
    """

    def __init__(self, path: str) -> None:
        
        self.path = path
        
        image = cv2.imread(self.path)  # Load image
        self.pixels = np.array(image, dtype=float) / float(255)  # Convert to an array

        self.shape = self.pixels.shape
        self.height, self.width = list(map(int, self.shape[:2]))

    def show(self):
        """Show the AstroImage until any key is pressed.
        """

        cv2.namedWindow("AstroImage")
        cv2.imshow(self.path, self.pixels)
        cv2.waitKey(0)


def ndvi(image: AstroImage) -> np.ndarray:
    """Calculate NDVI on the given image.

    Return a numpy ndarray with a NDVI value for each pixel of the image.
    """

    blue, green, red = cv2.split(image.pixels)
    
    bottom = (red.astype(float) + blue.astype(float))
    bottom[bottom==0] = 0.01  # Avoid zero division error
    ndvi = (blue.astype(float) - red) / bottom
    
    return ndvi

def mean_ndvi(image: AstroImage) -> float:
    """ Calculate the mean NDVI value over all the pixels of the given image.

    Return a float representing the mean NDVI value of the image.
    """

    ndvi_array = ndvi(image)
    mean_ndvi = np.mean(ndvi_array)

    return mean_ndvi
