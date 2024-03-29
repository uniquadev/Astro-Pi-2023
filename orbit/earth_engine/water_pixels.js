// Load the CSV file containing the bounding box coordinates
var table = ee.FeatureCollection("REPLACE WITH YOUR TABLE");

// Define a function to calculate NDWI
var calculateNDWI = function(image) {
  var ndwi = image.normalizedDifference(['B3', 'B5']);
  return image.addBands(ndwi.rename('NDWI'));
};

// Load Landsat 8 image collection and filter by date and location
var collection = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
  .filterDate('2015-01-01', '2015-12-31')
  .map(calculateNDWI);

// Define a water threshold
var waterThreshold = 0.2;

// Function to check if a point is on water
var checkPointOnWater = function(point) {
  // Calculate mean NDWI for the region of interest
  var meanNDWI = collection.mean().select('NDWI');
  
  // Create a binary water mask
  var waterMask = meanNDWI.gt(waterThreshold);
  
  // Check if the point is on water
  var isOnWater = waterMask.sample(point, 30).first().get('NDWI');
  
  // Return the result
  return ee.Feature(point).set('isOnWater', isOnWater);
};

// Map over the table rows
var processedData = table.map(function(row) {
  var name = row.get('name'); // Assuming the first feature is the name
  var xmin = ee.Number.parse(row.get('xmin'));
  var ymin = ee.Number.parse(row.get('ymin'));
  var xmax = ee.Number.parse(row.get('xmax'));
  var ymax = ee.Number.parse(row.get('ymax'));
  
  // Define the rectangle bounds
  var rectangle = ee.Geometry.Rectangle([
    xmin, ymin, xmax, ymax
  ]);
  
  // Calculate the area of the rectangle
  var area = rectangle.area();
  
  // Define the number of points and grid dimensions based on the area
  var totalPoints = 10; // Define the total number of points
  var gridWidth = ee.Number(area.sqrt()).ceil();
  var gridHeight = gridWidth.divide(totalPoints).ceil();
  
  // Generate uniformly distributed points across the rectangle
  var deltaX = xmax.subtract(xmin).divide(gridWidth);
  var deltaY = ymax.subtract(ymin).divide(gridHeight);
  
  var points = ee.FeatureCollection(
    ee.List.sequence(0, gridWidth.subtract(1)).map(function(x) {
      var xCoord = xmin.add(deltaX.multiply(x));
      return ee.List.sequence(0, gridHeight.subtract(1)).map(function(y) {
        var yCoord = ymin.add(deltaY.multiply(y));
        var lonLat = ee.Geometry.Point([xCoord, yCoord]).transform('EPSG:4326');
        return ee.Feature(lonLat);
      });
    }).flatten()
  );
  
  // Check if the points are on water
  var pointsOnWater = points.map(checkPointOnWater);
  // Return the processed data
  return row.set('name', name).set('pointsOnWater', pointsOnWater);
});

// Print the processed data
print('Processed Data:', processedData);
