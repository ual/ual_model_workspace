import osmnx as ox
import os
import requests
import zipfile
import geopandas as gpd

ox.config(use_cache=True, log_console=True, data_folder='../data')

# point to the shapefile for counties
counties_shapefile_url = 'http://www2.census.gov/geo/tiger/' + \
    'GENZ2016/shp/cb_2016_us_county_500k.zip'

# identify bay area counties by fips code
bayarea = {'Alameda': '001',
           'Contra Costa': '013',
           'Marin': '041',
           'Napa': '055',
           'San Francisco': '075',
           'San Mateo': '081',
           'Santa Clara': '085',
           'Solano': '095',
           'Sonoma': '097'}

counties_shapefile_zip = counties_shapefile_url[
    counties_shapefile_url.rfind('/') + 1:]
counties_shapefile_dir = counties_shapefile_zip[
    : counties_shapefile_zip.rfind('.zip')]
if not os.path.exists(counties_shapefile_dir):
    response = requests.get(counties_shapefile_url)
    with open(counties_shapefile_zip, 'wb') as f:
        f.write(response.content)
        with zipfile.ZipFile(counties_shapefile_zip, 'r') as zip_file:
            zip_file.extractall(counties_shapefile_dir)
    os.remove(counties_shapefile_zip)

counties = gpd.read_file(counties_shapefile_dir)

# retain only those tracts that are in the bay area counties
mask = (counties['STATEFP'] == '06') & (counties['COUNTYFP'].isin(
    bayarea.values()))
gdf_bay = counties[mask]

bayarea_polygon = gdf_bay.unary_union

# get the convex hull, otherwise we'll cut out bridges over the bay
bayarea_polygon = bayarea_polygon.convex_hull
bayarea_polygon_proj, crs = ox.project_geometry(bayarea_polygon)

# get the simplified graph
G = ox.graph_from_polygon(bayarea_polygon, network_type='all', simplify=True)

# convert to two-way
H = ox.get_undirected(G)

# save graph as OSM
ox.save_graph_osm(
    G, oneway=False, filename='bay_area_full_2_way_network_simplified.osm')
