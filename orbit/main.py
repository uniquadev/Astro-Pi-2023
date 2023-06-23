import sys
import cv2
import json

from logzero import logger, logfile
from pathlib import Path

from utils.ndvi import mean_ndvi
from utils.vci import vci_calculate, vci_classify


# --------------------------------------
# VARIABLES
# --------------------------------------

# Resolve absolute path to the current code directory
base_folder: Path = Path(__file__).parent.resolve()

# Set log file
logfile(base_folder / "main.log", backupCount=0, maxBytes=30e6)


def load_json_data(path: str):
    with open(path, "r") as f:
        data = json.loads(f.read())["features"]
        result = {feature["properties"]["path"][3:]: feature["properties"]["mean_ndvi"] for feature in data}

        return result


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

    filtered_images = {str(image_path): cv2.imread(str(image_path)) for image_path in path.iterdir()}
    logger.info(f"{len(filtered_images)}, images loaded")

    # Calculate average NDVI not including cloud pixels which have negative NDVI values
    latest_ndvi = {image_path: mean_ndvi(image, remove_negatives=True) for image_path, image in filtered_images.items()}
    
    logger.info("Average NDVI values calculated for each image")
    
    ndvi_2019 = load_json_data("./past_ndvi_data/2019_ndvi.json")
    ndvi_2020 = load_json_data("./past_ndvi_data/2020_ndvi.json")
    ndvi_2021 = load_json_data("./past_ndvi_data/2021_ndvi.json")
    ndvi_2022 = load_json_data("./past_ndvi_data/2022_ndvi.json")

    historic_ndvi = [ndvi_2019, ndvi_2020, ndvi_2021, ndvi_2022]

    logger.info("Loaded ndvi values from past years")

    ndvi_by_roi = {roi: [] for roi, _ in filtered_images.items()}
    
    for year in historic_ndvi:
        for roi, ndvi in year.items():
            ndvi_by_roi[roi].append(ndvi)

    for roi, ndvi in latest_ndvi.items():
        ndvi_by_roi[roi].append(ndvi)

    min_max_ndvi_by_roi = {roi: (min(ndvi_values), max(ndvi_values)) for roi, ndvi_values in ndvi_by_roi.items()}

    vci_by_roi = {roi: vci_calculate(latest_ndvi[roi], min, max) for roi, (min, max) in min_max_ndvi_by_roi.items()}
    vci_classes_by_roi = {roi: vci_classify(vci) for roi, vci in vci_by_roi.items()}

    # Save results
    with open("main_results.txt", "w+") as f:
        f.write("LATEST NDVI\n")
        f.write(str(latest_ndvi)+"\n")
        f.write("NDVI BY ROI OVER YEARS (2019-2023)\n")
        f.write(str(ndvi_by_roi)+"\n")
        f.write("VCI BY ROI\n")
        f.write(str(vci_by_roi)+"\n")
        f.write("VCI CLASSES BY ROI\n")
        f.write(str(vci_classes_by_roi))

    logger.info("Completed")

if __name__ == "__main__":
    main(len(sys.argv), sys.argv)
