# --------------------------------------
# IMPORTS
# --------------------------------------

from pathlib import Path  # Path utilities
import sys # System-specific parameters and functions
import shutil # High-level file operations

from logzero import logger, logfile  # Debug purposes
from datetime import datetime, timedelta  # Time recognition
from utils.gsd import gsd # Ground sampling distance
from utils.ndvi import ndvi, mean_ndvi # Normalized Difference Vegetation Index
from utils.classifiers import OtsuThresholdClassifier, ThresholdClassifier, NDVIClassifier, DarkImageClassifier # Classifiers

# --------------------------------------
# CONSTANTS
# --------------------------------------

SENSOR_WIDTH = 6.2928  # mm
SENSOR_HEIGHT = 4.712  # mm
FOCAL_LENGTH = 4.735  # mm
IMAGE_WIDTH = 4056  # pixels
IMAGE_HEIGHT = 3040  # pixels

DARK_THRESHOLD = 30
THRESHOLD = 26
PIXEL_THRESHOLD = 0.76
NDVI_RANGE = [-1, 0.1]
NDVI_THRESHOLD = 32.2

# --------------------------------------
# VARIABLES
# --------------------------------------

# Defining initial time variables to know when to stop the program
start_time: datetime = datetime.now()

# Resolve absolute path to the current code directory
base_folder: Path = Path(__file__).parent.resolve()

# Define output folder for images
out_folder = base_folder / "out"
shutil.rmtree(out_folder, ignore_errors=True)

# Set log file
logfile(base_folder / "filter.log", backupCount=0, maxBytes=30e6)

# entry point
def main(argc, argv):

    # Check command-line arguments
    if argc != 2:
        logger.error("Usage: orbit <path>")
        sys.exit(1)
    
    # Get the path to the folder containing the images
    path = Path(argv[1])

    # Check if the path exists
    if not path.exists():
        logger.error("Path not found")
        sys.exit(1)

    image_counter = len(list(path.glob("*.jpg")))
    logger.info(f"Found {image_counter} images")
    
    # IMAGE PROCESSING
    # 1) Remove black pictures
    dark_out = out_folder / "dark_out"
    dark_out.mkdir(parents=True, exist_ok=True)

    dark_cls = DarkImageClassifier(path, dark_out)
    dark_cls.start(DARK_THRESHOLD)

    filtered = len(list(dark_out.glob("*.jpg")))
    logger.info(f"Removed {image_counter - filtered} dark images")
    image_counter = filtered

    # 2) Remove images with cloud coverage through Thresholding
    threshold_out = out_folder / "threshold_out"
    threshold_out.mkdir(parents=True, exist_ok=True)

    threshold_cls = ThresholdClassifier(dark_out, threshold_out)
    threshold_cls.start(PIXEL_THRESHOLD, THRESHOLD)

    filtered = len(list(threshold_out.glob("*.jpg")))
    logger.info(f"Removed {image_counter - filtered} cloudy images")
    image_counter = filtered
    shutil.rmtree(dark_out, ignore_errors=True)

    # 3) Remove images with sea coverage through NDVI
    ndvi_out = out_folder / "ndvi_out"
    ndvi_out.mkdir(parents=True, exist_ok=True)

    ndvi_cls = NDVIClassifier(threshold_out, ndvi_out)
    ndvi_cls.start(NDVI_RANGE, NDVI_THRESHOLD)

    filtered = len(list(ndvi_out.glob("*.jpg")))
    logger.info(f"Removed {image_counter - filtered} sea images")
    image_counter = filtered
    shutil.rmtree(threshold_out, ignore_errors=True)
    
    logger.info(f"execution completed in {(datetime.now() - start_time)}, with {image_counter} images")

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)



# Remove images with cloud coverage higher than 20%
# Remove images taken over sea
# Calculate mean ndvi
# Calculate vci

"""
 ____  _                ____             
|  _ \(_)__________ _  |  _ \  _____   __
| |_) | |_  /_  / _` | | | | |/ _ \ \ / /
|  __/| |/ / / / (_| | | |_| |  __/\ V / 
|_|   |_/___/___\__,_| |____/ \___| \_/  

"""
