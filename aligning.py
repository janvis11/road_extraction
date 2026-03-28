#  while creating the road mask we extract some roads from the OSM data , many times this data is not updated and the roads are not aligned with the satellite imagery. To align the roads with the satellite imagery we can use the following code. 
import geopandas as gpd
from shapely.affinity import translate

VEC = r"C:\Users\admin\Desktop\janvi\city\262189411\roadd.shp"
OUT = r"C:\Users\admin\Desktop\janvi\city\262189411\road_utm_aligned.shp"

dx = 8.0
dy = 0.0

gdf = gpd.read_file(VEC)
gdf = gdf.to_crs(32644)

gdf.geometry = gdf.geometry.apply(lambda g: translate(g, xoff=dx, yoff=dy))

gdf = gdf.to_crs(4326)
gdf.to_file(OUT, driver="GPKG")