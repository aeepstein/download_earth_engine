import ee
from datetime import datetime

# Authenticate and initialize Earth Engine
ee.Authenticate()
ee.Initialize()

# Define region of interest (ROI) for Africa
roi = ee.Geometry.Rectangle([-20, -35, 55, 38])  # Approximate bounding box of Africa

# Load MODIS LST dataset
dataset = ee.ImageCollection('MODIS/061/MOD11A1').select('LST_Day_1km')

# Convert LST from Kelvin to Celsius and scale it
def kelvin_to_celsius(image):
    return image.multiply(0.02).subtract(273.15).copyProperties(image, image.propertyNames())

# Apply conversion
dataset = dataset.map(kelvin_to_celsius)

# Range of years to process
start_year = 2015
end_year = 2023

# Loop through years and months
for year in range(start_year, end_year + 1):  # Loop from 2015 to 2023
    for month in range(1, 13):  # Loop through months
        start_date = f"{year}-{month:02d}-01"
        end_date = (datetime(year, month % 12 + 1, 1) if month < 12 else datetime(year + 1, 1, 1)).strftime("%Y-%m-%d")
        
        # Create a monthly composite and clip to Africa
        monthly_image = dataset.filterDate(start_date, end_date).mean().clip(roi)
        
        # Export to Google Drive
        task = ee.batch.Export.image.toDrive(
            image=monthly_image,
            description=f'LST_Africa_{year}_{month:02d}',
            folder='LST_Monthly',  # Change to your desired Drive folder
            scale=5000,  # Resolution in meters
            region=roi.bounds().getInfo()['coordinates'],  # Corrected region format
            maxPixels=1e13
        )
        task.start()
        print(f"Export started for {year}-{month:02d}")

