import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set a modern style using seaborn
sns.set_style("whitegrid")
sns.set_palette("colorblind")

# DATA HERE
years = [str(year) + "/04" for year in range(2019, 2024)]
ndvi_values = [0.2904903973013246, 0.006993930524487433, 0.05946905302361119, -0.011637350923399332, 0.049035084591179764]

# Calculate the mean value
mean_ndvi = np.mean(ndvi_values)

# Create a figure and axes with custom figsize
fig, ax = plt.subplots(figsize=(8, 6))

# Plot the line with markers
sns.lineplot(x=years, y=ndvi_values, marker='o', ax=ax)

# Plot the mean line
ax.axhline(y=mean_ndvi, color='#fbbb04', linestyle='--', label='Mean NDVI')

# Customize the plot
ax.set_xlabel('Year', fontsize=12)
ax.set_ylabel('NDVI Value', fontsize=12)
ax.set_title('NDVI Evolution', fontsize=14)

# Set the x-axis and y-axis limits
ax.set_xlim(years[0], years[-1])
ax.set_ylim(min(ndvi_values) - 0.1, max(ndvi_values) + 0.1)

# Change the grid background color to light blue
ax.set_facecolor('#e6f2ff')

# Change the grid lines color to white
ax.grid(color='white')

# Add a horizontal line at y=0.5
ax.axhline(y=0.5, color='gray', linestyle='--', alpha=0.7)

# Add data labels to the markers
for i in range(len(years)):
    ax.text(years[i], ndvi_values[i], f'{ndvi_values[i]:.2f}', ha='center', va='bottom')

# Show the legend
ax.legend()

# Show the plot
plt.tight_layout()
plt.show()
