// Read the CSV file
var roiTable = ee.FeatureCollection("projects/ee-diegoromeo025/assets/bounding_boxes")

// Define a function to calculate NDVI for a single ROI
var calculateMeanNdvi = function(feature) {
  // Get the ROI properties from the feature
  var roiName = ee.String(feature.get('path'));
  var xmin = ee.Number(feature.get('xmin'));
  var ymin = ee.Number(feature.get('ymin'));
  var xmax = ee.Number(feature.get('xmax'));
  var ymax = ee.Number(feature.get('ymax'));

  // Define the region of interest (bounding box)
  var roi = ee.Geometry.Rectangle([xmin, ymin, xmax, ymax]);

  // Define the month of interest
  var year = 2021;  // Replace with your desired year
  var month = 4;    // Replace with your desired month

  // Filter the Sentinel-2 Level-2A collection by month and region
  var collection = ee.ImageCollection('COPERNICUS/S2_SR')
    .filter(ee.Filter.calendarRange(year, year, 'year'))
    .filter(ee.Filter.calendarRange(month, month, 'month'))
    .filterBounds(roi)
    .select(['B8', 'B4'])  // Select the necessary spectral bands for NDVI calculation ('B8' and 'B4')
    .first();  // Limit to only the first image in the collection

  // Calculate NDVI for the selected image
  var ndvi = collection.normalizedDifference(['B8', 'B4']).rename('NDVI');

  // Calculate the mean NDVI over the region of interest
  var meanNdviValue = ndvi.reduceRegion({
    reducer: ee.Reducer.mean(),
    geometry: roi,
    scale: 10,
    maxPixels: 1e13,
    bestEffort: true
  }).get('NDVI');

  // Create a new feature with the mean NDVI value and ROI name
  var featureWithNdvi = ee.Feature(roi, { 'path': roiName, 'mean_ndvi': meanNdviValue });

  return featureWithNdvi;
};

// Apply the calculation for each ROI in the table
var roiWithNdvi = roiTable.map(calculateMeanNdvi);

// Print the resulting features with mean NDVI values
print(roiWithNdvi);
