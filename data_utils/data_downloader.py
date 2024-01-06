import argparse
import json
import logging
import os
import sys
import urllib
import urllib.request
from argparse import ArgumentParser
from urllib.error import HTTPError

import geopandas as gpd

DEFAULT_DATA_LINK = 'https://raw.githubusercontent.com/tbrugz/geodata-br/master/geojson/geojs-31-mun.json'

# Creating basic log configuration
logging.basicConfig(
    format='[%(asctime)s] - %(levelname)-4s - %(filename)s - %(lineno)d: %(message)s',
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)])

# Retrieving logging object
logger = logging.getLogger(__name__)


def read_data(args):
    """Reads the data from an online URL and converts it to a GeoPandas DataFrame.

    Args:
        args (argparse.Namespace): Command line arguments.

    Returns:
        (gpd.GeoDataFrame): Output GeoDataFrame containing all the data in tabular format.
    """

    logger.info(f'Downloading data from: {args.data_link}')
    try:
        with urllib.request.urlopen(args.data_link) as response:
            body = response.read()
    except HTTPError:
        logger.error('Invalid input URL! Data not found')
    else:
        logger.info(f'Data file {args.file_name} successfully saved in {args.dest_path}')

    logger.info('Parsing data with GeoPandas')
    return gpd.read_file(body.decode('utf-8'), driver='GeoJSON')


def save_data_to_file(args, gdf):
    """Save data to output .geojson file according to the dest_path and file_name passed as arguments.

    Args:
        args (argparse.Namespace): Command line arguments.
        gdf (gpd.GeoDataFrame): GeoDataFrame containing all the data in tabular format.

    Returns:
        (None)
    """
    output_path = os.path.join(args.dest_path, args.file_name)
    logger.info(f'Saving data to output path: {output_path}')
    with open(output_path, 'w') as geojson_file:
        json.dump(gdf.to_json(), geojson_file, indent=4)


def main():
    """
    Main function that will do the following steps, in order:
        - Download Geographic data from a web URL
        - Parse the data from bytes to GeoDataFrame
        - Changes the coordinates projection to 'EPSG:31983'
        - Calculates the area in [km^2] for all counties
        - Saves the calculated area in a separate column called 'area'
        - Stores the data in a .geojson file

    Returns:
        (None): Saves the data file with the --file-name in the specified --dest-path.
    """
    parser = ArgumentParser()
    parser.add_argument(
        '--data-link', default=DEFAULT_DATA_LINK, help='The link to the dataset.')
    parser.add_argument(
        '--dest-path', default='../dados', help='Destination path where the dataset will be saved.')
    parser.add_argument(
        '--file-name', default='municipios-mg.geojson', help='Output file name with extension.'
    )
    logger.info('Parsing command line arguments')
    args = parser.parse_args()

    gdf_mg_counties = read_data(args)
    logger.info('Setting coordinates to EPSG:31983')
    gdf_mg_counties['geometry'] = gdf_mg_counties['geometry'].to_crs('EPSG:31983')
    # Area in [km^2]
    gdf_mg_counties['area'] = gdf_mg_counties['geometry'].area / 1e6
    save_data_to_file(args, gdf_mg_counties)


if __name__ == '__main__':
    main()
