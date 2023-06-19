import cv2
import sys
import numpy as np

from utils.ndvi import ndvi

from utils.classifiers import resize_img

image = cv2.imread(sys.argv[1], cv2.IMREAD_COLOR)
image_pixels = np.array(image, dtype=float) / float(255)

total_pixels = image_pixels.size
ndvi_values = ndvi(image_pixels)
pixel_count = np.count_nonzero((ndvi_values < 0.1) & (ndvi_values > -1))

percentage = round((pixel_count / total_pixels) * 100, 1)

# Display the thresholded image
print(percentage)
cv2.imshow('Thresholded Image', resize_img(image, 0.2))
cv2.waitKey(0)
cv2.destroyAllWindows()

# 