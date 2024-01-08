import logging
import os
import sys

import geopandas as gpd
import pandas as pd

# Creating basic log configuration
logging.basicConfig(
    format='[%(asctime)s] - %(levelname)-4s - %(filename)s - %(lineno)d: %(message)s',
    level=logging.DEBUG,
    handlers=[logging.StreamHandler(stream=sys.stdout)])

# Retrieving logging object
logger = logging.getLogger(__name__)


def merge_datasets(dataset1_path, dataset2_path, dest_path, file_name):
    """
        Function that will read two data sets and join them in the axis 0 (append operation).
        The data sets will contain geographic data so GeoPandas will be used to parse them.

    Args:
        dataset1_path (str): Path to the first data set to be merged.
        dataset2_path (str): Path to the second data set to be merged.
        dest_path (str): Destination path where the merged dataset will be saved.
        file_name (str): Output file name with .geojson extension.

    Returns:
        (None): Saves the merged data frame with --file-name in the specified --dest-path.
    """

    logger.info('Reading dataset 1')
    gdf1 = gpd.read_file(dataset1_path)
    logger.info('Reading dataset2')
    gdf2 = gpd.read_file(dataset2_path)
    logger.info('Filtering common columns')
    common_cols = gdf1.columns.intersection(gdf2.columns)
    assert not common_cols.empty, 'Both dataframes must have common columns in order to merge them!'
    gdf_merged = gpd.GeoDataFrame(pd.concat([gdf1[common_cols], gdf2[common_cols]], axis=0))
    gdf_merged.geometry = gdf_merged.geometry.to_crs('EPSG:31983')
    output_path = os.path.join(dest_path, file_name)
    logger.info(f'Saving data to output path: {output_path}')
    gdf_merged.to_file(output_path, driver='GeoJSON')
