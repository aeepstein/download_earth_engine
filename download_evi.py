import ee
import geemap
import os
import datetime

ee.Initialize()

africa_geometry = ee.Geometry.Polygon([
    [[-20, 40], [60, 40], [60, -40], [-20, -40], [-20, 40]]
])

def add_evi(image):
    evi = image.expression(
        '2.5 * ((NIR - RED) / (NIR + 6 * RED - 7.5 * BLUE + 1))', {
            'NIR': image.select('B8'),   # Sentinel-2 NIR
            'RED': image.select('B4'),   # Sentinel-2 RED
            'BLUE': image.select('B2')   # Sentinel-2 BLUE
        }).rename('EVI')
    return image.addBands(evi)

start_year = 2021
end_year = 2024

s2_sr = ee.ImageCollection("COPERNICUS/S2_SR")

output_dir = "evi_rasters_africa"
os.makedirs(output_dir, exist_ok=True)

for year in range(start_year, end_year + 1):
    for month in range(1, 13):
        start_date = datetime.datetime(year, month, 1)
        end_date = (start_date + datetime.timedelta(days=31)).replace(day=1)

        monthly_collection = (
            s2_sr.filterBounds(africa_geometry)
                 .filterDate(start_date, end_date)
                 .map(add_evi)  # Add EVI band
                 .select('EVI')
                 .mean()
                 .clip(africa_geometry)
        )

        file_name = f"evi_{year}_{month:02d}.tif"
        file_path = os.path.join(output_dir, file_name)

        print(f"Starting export for {file_name}...")
        task = ee.batch.Export.image.toDrive(
            image=monthly_collection,
            description=file_name,
            folder="evi_africa",
            fileNamePrefix=file_name.split('.')[0],
            region=africa_geometry,
            scale=1000,  # Resolution in meters
            maxPixels=1e13
        )
        task.start()

        print(f"Export task started for {file_name}")

print("All exports have been submitted.")
