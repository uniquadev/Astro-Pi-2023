from PIL import Image
from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import matplotlib.cm as cm
from fastiecm import fastiecm

colormap = ListedColormap(fastiecm / 255)

# Open the image
image_path = './images/fastiecm_img5.jpg'  # Replace with the actual path to your image
image = Image.open(image_path)

# Rotate the image by 45 degrees
rotated_image = image.rotate(-10, expand=True)


# Create a figure and axes with custom figsize
fig, ax = plt.subplots(figsize=(9, 8))

# Apply the rotation transformation to the axes
trans = transforms.Affine2D().rotate_deg(-10)
ax.set_transform(trans)

# Calculate the padding for the rotated image
width, height = rotated_image.size
pad_x = (width - image.width) / 2
pad_y = (height - image.height) / 2

# Display the rotated image with padding and spectral colormap
im = ax.imshow(rotated_image, extent=(-pad_x, image.width + pad_x, -pad_y, image.height + pad_y), cmap=colormap, vmin=-1, vmax=1)

# Hide the axis labels and ticks
ax.axis('off')

# Set the title
ax.set_title('NDVI Image', fontsize=14)

# Add a colorbar
cax = fig.add_axes([0.92, 0.25, 0.02, 0.5])  # Position of the colorbar
cbar = plt.colorbar(im, cax=cax)

# Set the label for the colorbar
cbar.set_label('NDVI')

# Adjust the layout to prevent overlap
plt.tight_layout(rect=[0, 0, 0.9, 1])

# Show the plot
plt.show()
