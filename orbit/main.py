import os

from utils.gsd import gsd
from utils.ndvi import ndvi, mean_ndvi
from utils.classifiers import OtsuThresholdClassifier, ThresholdClassifier, NDVIClassifier

SENSOR_WIDTH = 6.2928  # mm
SENSOR_HEIGHT = 4.712  # mm
FOCAL_LENGTH = 0  # mm
IMAGE_WIDTH = 4056  # pixels
IMAGE_HEIGHT = 3040  # pixels


# IMAGE PROCESSING
# Remove black pictures



# Remove images with cloud coverage higher than 20%



# Remove images taken over sea


# Calculate mean ndvi



# Calculate vci
