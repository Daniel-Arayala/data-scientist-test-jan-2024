import logging
import os
import sys
import urllib
import urllib.request
from urllib.error import HTTPError

import geopandas as gpd


# Creating basic log configuration
logging.basicConfig(
    format='[%(asctime)s] - %(levelname)-4s - %(filename)s - %(lineno)d: %(message)s',
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)])

# Retrieving logging object
logger = logging.getLogger(__name__)


def read_data(data_url):
    """Reads the data from an online URL and converts it to a GeoPandas DataFrame.

    Args:
       data_url (str): URL to the data set.

    Returns:
        (gpd.GeoDataFrame): Output GeoDataFrame containing all the data in tabular format.
    """

    logger.info(f'Downloading data from: {data_url}')
    try:
        with urllib.request.urlopen(data_url) as response:
            body = response.read()
    except HTTPError:
        logger.error('Invalid input URL! Data not found')
    else:
        logger.info(f'Data was retrieved from the url')

    logger.info('Parsing data with GeoPandas')
    return gpd.read_file(body.decode('utf-8'), driver='GeoJSON')


def download_data_from_url(data_url, dest_path, file_name):
    """
      Downloader function that will do the following steps, in order:
        - Download Geographic data from a web URL
        - Parse the data from bytes to GeoDataFrame
        - Changes the coordinates projection to 'EPSG:31983'
        - Calculates the area in [km^2] for all counties
        - Saves the calculated area in a separate column called 'area'
        - Stores the data in a .geojson file
    Args:
        data_url (str): URL to the data set.
        dest_path (str): Destination path where the dataset will be saved.
        file_name (str): Output file name with .geojson extension.
        
    Returns:
        (None): Saves the data file with the file_name in the specified dest_path.
    """

    gdf_mg_counties = read_data(data_url)
    logger.info('Setting coordinates to EPSG:31983')
    gdf_mg_counties['geometry'] = gdf_mg_counties['geometry'].to_crs('EPSG:31983')
    # Area in [km^2]
    gdf_mg_counties['area'] = gdf_mg_counties['geometry'].area / 1e6
    output_path = os.path.join(dest_path, file_name)
    logger.info(f'Saving data to output path: {output_path}')
    gdf_mg_counties.to_file(output_path, driver='GeoJSON')
