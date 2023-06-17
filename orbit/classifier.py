import cv2
import numpy as np

# Load the NIR image using OpenCV
nir_image = cv2.imread('../out/img_0000.jpg', cv2.IMREAD_COLOR)

# Extract the NIR channel (e.g., green channel)
nir_channel = nir_image[:, :, 1]  # Green channel index is 1

# Set the threshold for water detection
threshold = 0.8

# Convert NIR channel to binary water mask
_, cloud_mask = cv2.threshold(nir_channel, int(threshold * 255), 255, cv2.THRESH_BINARY)

screen_width = 800  # Adjust the screen width as desired
scale_factor = min(screen_width / nir_image.shape[1], 1.0)
resized_nir = cv2.resize(nir_image, None, fx=scale_factor, fy=scale_factor)
resized_cloud_mask = cv2.resize(water_mask, None, fx=scale_factor, fy=scale_factor)

# Create a red-colored mask
red_mask = np.zeros_like(resized_nir)
red_mask[:, :, 2] = resized_cloud_mask  # Set the red channel of the mask to the cloud mask


# Calculate the total number of pixels
total_pixels = resized_cloud_mask.size

# Count the number of cloud pixels
cloud_pixel_count = np.count_nonzero(resized_cloud_mask)

# Calculate the percentage of cloud pixels
cloud_percentage = (cloud_pixel_count / total_pixels) * 100

# Print the number of pixels covered by clouds and the total percentage
print("Water Pixels: ", cloud_pixel_count)
print("Total Pixels: ", total_pixels)
print("Water Percentage: ", cloud_percentage)


# Display the resized NIR image and the red-colored mask
cv2.imshow('Resized NIR Image', resized_nir)
cv2.imshow('Red Water Mask', red_mask)
cv2.waitKey(0)
cv2.destroyAllWindows()
