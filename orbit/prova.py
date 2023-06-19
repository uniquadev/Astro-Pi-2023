import cv2

from utils.classifiers import resize_img

# Load the NIR image
nir_image = cv2.imread('../out/img_0375.jpg', cv2.IMREAD_GRAYSCALE)

nir_image = resize_img(nir_image, 0.2)

# Apply Otsu's thresholding
_, thresholded = cv2.threshold(nir_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Display the thresholded image
cv2.imshow('Thresholded Image', thresholded)
cv2.waitKey(0)
cv2.destroyAllWindows()
