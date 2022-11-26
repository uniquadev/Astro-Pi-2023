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

# --------------------------------------
# CONSTANTS
# --------------------------------------
RUN_TIME = timedelta(minutes=179) # How long to run the program for

# --------------------------------------
# VARIABLES
# --------------------------------------

# images counters
image_counter = 0
image_size = 0

# Defining initial time variables to know when to stop the program
start_time = datetime.now()
now_time = datetime.now()

# Resolve absolute path to the current code directory
base_folder = Path(__file__).parent.resolve()
# Define output folder
out_folder = base_folder / "out"
out_folder.mkdir(parents=True, exist_ok=True)

# Set log file
logfile(base_folder / "astro.log", backupCount=0, maxBytes=1e6)

# Camera settings - max res for more precise indices
camera = PiCamera()
camera.resolution = (4056,3040)

# --------------------------------------
# FUNCTIONS
# --------------------------------------

# --------------------------------------
# ENTRY
# --------------------------------------

logger.info('started')
# run untile the program has been running for the specified RUN_TIME
while now_time - start_time < RUN_TIME:
    print(f'\rElapsed time: {now_time - start_time}', end='')
    # Update time
    now_time = datetime.now()
    # TODO Check storage limit
    # Ensure errors don't break anything
    try:
      # TODO Check light conditions
      # TODO Take picture
      # TODO Filter picture
      # TODO Store picture data
      # TODO Save picture & Increment counters
      pass
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
logger.info('ended')
camera.close()