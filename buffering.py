import geopandas as gpd
import os

print("----- Road Buffering Script Started -----\n")

# ---- FILE PATHS ----
input_file = r"C:\Users\admin\Desktop\janvi\hyderabad\processing\road_utm_aligned.shp"
output_file = r"C:\Users\admin\Desktop\janvi\hyderabad\processing\road_utm_buffered.shp"
# --------------------

print("Step 1: Checking if input file exists...")

if not os.path.exists(input_file):
    print("   ❌ ERROR: Input file not found.")
    exit()

print("   ✔ Input file found.")

print("\nStep 2: Creating output directory if it does not exist...")

output_folder = os.path.dirname(output_file)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)
    print(f"   ✔ Output folder created at: {output_folder}")
else:
    print("   ✔ Output folder already exists.")

print("\nStep 3: Reading input shapefile...")
gdf = gpd.read_file(input_file)
print("   ✔ File loaded successfully.")

print("\nStep 4: Checking Coordinate Reference System (CRS)...")
print(f"   Current CRS: {gdf.crs}")

if gdf.crs and gdf.crs.is_geographic:
    print("   CRS is geographic (degrees). Reprojecting to UTM Zone 43N (EPSG:32643)...")
    gdf = gdf.to_crs(epsg=32643)
    print("   ✔ Reprojection completed.")
else:
    print("   CRS is already projected (meters) or undefined.")

print("\nStep 5: Applying buffer distance logic based on road type...")

def get_buffer_distance(road_type):
    road_type = str(road_type).lower()
    if road_type == "trunk":
        return 12
    elif road_type == "primary":
        return 8
    elif road_type == "secondary":
        return 6
    elif road_type == "tertiary":
        return 4
    elif road_type == "residential":
        return 3
    else:
        return 2

# Check if 'highway' column exists
if "highway" not in gdf.columns:
    print("   ❌ ERROR: 'highway' column not found in attribute table.")
    print("   Available columns are:", gdf.columns)
    exit()

print("   ✔ 'highway' column found.")

gdf["buffer_dist"] = gdf["highway"].apply(get_buffer_distance)

print("   ✔ Buffer distances assigned.")
print(gdf[["highway", "buffer_dist"]].head())

print("\nStep 6: Creating buffer geometries...")
gdf["geometry"] = gdf.buffer(gdf["buffer_dist"])
print("   ✔ Buffer geometries created.")

print("\nStep 7: Saving buffered shapefile...")
gdf.to_file(output_file)
print(f"   ✔ Output saved successfully at: {output_file}")

print("\n----- Buffering Completed Successfully -----")