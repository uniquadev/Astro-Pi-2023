"""Main file

This script will run aboard the ISS taking pictures of the Earth surface if there is enough light.
Every time a photo is taken, the script will automatically determine the average NIR (Near InfraRed) value of the image to decide whether to discard or keep it depending if it is over water or clouds.
In the first case the image will be eventually overwritten by a new image while in the second case the program will proceed normally.
The program will also save for each image the ISS location at the time it was taken, and the time itself as metadata.

The script will automatically stop before the 3 hours of maximum allowed runtime have passed.
"""

# --------------------------------------
# IMPORTS
# --------------------------------------
from picamera import PiCamera # Take images
from pathlib import Path # Path utilities
from datetime import datetime, timedelta # Time recognition
from logzero import logger, logfile # Debug purposes
from time import sleep # Sleep
import exif # Embed GPS data into any images
from os import fsync # Flush data to disk
from orbit import ISS, ephemeris # Load the JPL ephemeris DE421 (covers 1900-2050).
from skyfield.api import load # Load timescale data
import numpy as np # Array manipulation
import cv2 # Image processing

# --------------------------------------
# CONSTANTS
# --------------------------------------
RUN_TIME = timedelta(minutes=177) # How long to run the program for

# Sets comparative value for if an image has too much water/cloud
# A good range is 40-50 / 90-100
WATER_THRESHOLD = 43
CLOUD_THRESHOLD = 100

# --------------------------------------
# VARIABLES
# --------------------------------------

# images counters
image_counter = 0
astro_memory = 30e6 # 30 MB used for logzero

# Defining initial time variables to know when to stop the program
start_time = datetime.now()
now_time = datetime.now()

# Resolve absolute path to the current code directory
base_folder = Path(__file__).parent.resolve()
# Define output folder
out_folder = base_folder / "out"
out_folder.mkdir(parents=True, exist_ok=True)

timescale = load.timescale()

# Set log file
logfile(base_folder / "astro.log", backupCount=0, maxBytes=30e6)

# Camera settings - max res for more precise indices
camera = PiCamera()
camera.resolution = (4056,3040)

# --------------------------------------
# FUNCTIONS
# --------------------------------------

def light_level() -> bool:
  """
  Check if the light level is sufficient for the camera to take a picture

  Return a boolean value indicating if the light level is sufficient or not.
  """

  curr = timescale.now()
    
  if ISS.at(curr).is_sunlit(ephemeris):
      return True
  
  else:
      return False


def convert_cords(angle) -> tuple[bool, str]:
    """
    Convert a `skyfield` Angle to an EXIF-appropriate
    representation (positive rationals)
    e.g. 98° 34' 58.7 to "98/1,34/1,587/10"

    Return a tuple containing a boolean and the converted angle,
    with the boolean indicating if the angle is negative.
    """

    sign, degrees, minutes, seconds = angle.signed_dms()
    exif_angle = f'{degrees:.0f}/1,{minutes:.0f}/1,{seconds*10:.0f}/10'
    
    return sign < 0, exif_angle

def convert_time(time: datetime) -> str:
    """
    Convert a `datetime` object to an EXIF-appropriate representation (string)
    e.g. 2022-11-27 14:27:51.098019 to 2022:11:27 14:27:51

    Return a string containing the converted date/time.
    """

    return time.strftime("%Y:%m:%d %H:%M:%S")

def add_metadata(lat, latr, long, longr, t) -> None:
    """ Add the metadata tags to the camera
        so that we know the location and can identify the
        area on a map when we analyse the images on Earth.

        Time will also be saved for further analysis in Phase 4.
    """
    
    global camera
    
    # Location
    camera.exif_tags["GPS.GPSLatitude"] = lat
    camera.exif_tags["GPS.GPSLatitudeRef"] = latr
    camera.exif_tags["GPS.GPSLongitude"] = long
    camera.exif_tags["GPS.GPSLongitudeRef"] = longr

    # Time
    camera.exif_tags["DateTimeOriginal"] = t


def take_image() -> Path:
    """Take a picture, write metadata and return the path to the image"""
  
    global image_counter
    global now_time
  
    # Define output file
    out_file = out_folder / f"img_{image_counter:04d}.jpg"

    # Get location
    location = ISS.coordinates()
    south, exif_lat = convert_cords(location.latitude)
    west, exif_long = convert_cords(location.longitude)
    
    # Get time
    t = convert_time(now_time)

    # Add location and time 
    add_metadata(
      exif_lat,
      "S" if south else "N",
      exif_long,
      "W" if west else "E",
      t
    )

    # Take image
    camera.capture(str(out_file))

    # Flush data to disk
    fsync()

    return out_file

def is_useful(path:Path) -> bool:
  """ Checks to see if the image is over water/clouds
      so that we can delete it to save storage and processing
      because an image largely over water is useless for the task.
      The function takes the average light/darkness value and compares
      it to a known threshold to determine if the image is over water/clouds.

      Return a boolean value indicating if the image is useful or not.

      Original source coude at:
      https://github.com/SourishS17/Astro-Pi-2022/blob/db90b7ab1319c276c73f5d70addf7bae4b931a08/main.py#L100
  """
    
  image = cv2.imread(path).astype(np.float)
  nir_val = np.average(image[:, :, 0]) # Average Near Infrared value
  
  if CLOUD_THRESHOLD > nir_val > WATER_THRESHOLD:
      return True
  
  else:
      return False

# --------------------------------------
# ENTRY
# --------------------------------------

if __name__ == "__main__":

  logger.info('started')
  # run untile the program has been running for the specified RUN_TIME
  while now_time - start_time < RUN_TIME:

    now_time = datetime.now() # Update current time
    
    # Check storage limit, to don't surpass 3 GB in bytes
    if astro_memory >= 2.7e9:
      logger.error(f'Storage limit reached with {image_counter} images')
      break

    # Ensure errors don't break anything
    try:
      # Check if the light level is sufficient
      if light_level() == False:
        sleep(2)
        continue

      # Take picture
      path : Path = take_image()

      if is_useful(path) == False:
        # Sleep a short time to avoid taking pictures too slowly
        # Don't increment image counter as the image will be overwritten
        sleep(0.8)
        continue

      image_counter += 1
      astro_memory += path.stat().st_size

    except Exception as e:
      logger.exception(e)
      sleep(1) # Recover time
      image_counter += 2 # make error obvious

  """
    ____  _                ____             
  |  _ \(_)__________ _  |  _ \  _____   __
  | |_) | |_  /_  / _` | | | | |/ _ \ \ / /
  |  __/| |/ / / / (_| | | |_| |  __/\ V / 
  |_|   |_/___/___\__,_| |____/ \___| \_/  

  """
  logger.info(f'execution completed with {image_counter} images (づ ᴗ _ᴗ)づ')
  camera.close()
