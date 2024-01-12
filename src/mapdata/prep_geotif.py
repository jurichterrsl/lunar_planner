""" This file prepares the geotiff data."""
import math

### modules
#from osgeo import gdal, gdal_array, osr
import numpy as np
import matplotlib.pyplot as plt
import rasterio as rs
from rasterio.warp import transform, calculate_default_transform, Resampling
from pyproj import Proj, transform as pyproj_transform
from pyproj import CRS
import re


def analyse_geotiff_1band(path_to_tif):
    '''Quick script to analyse satellite data'''
    dataset = rs.open(path_to_tif)
    print("Size is {} x {} x {} (width x height x layers)".format(dataset.width,
                                                                  dataset.height,
                                                                  dataset.count))
    width = dataset.bounds.right-dataset.bounds.left
    height = dataset.bounds.top-dataset.bounds.bottom
    print("Width/ Height in m is {} / {}".format(width, height))

    print("Projection: ", dataset.crs)

    # Get reference lon & lat
    crs_dict = dataset.crs.to_dict()
    print(crs_dict)
    lonref = crs_dict['lon_0']
    latref = crs_dict['lat_0']
    radius = crs_dict['R']

    # Get extent of geotiff file
    lonmin = lonref - width/2 * 180/math.pi /radius
    lonmax = lonref + width/2 * 180/math.pi /radius
    latmin = latref - height/2 * 180/math.pi /radius
    latmax = latref + height/2 * 180/math.pi /radius

    print("Extent Lon - min: {}, max: {} ".format(lonmin, lonmax))
    print("Extent Lat - min: {}, max: {} ".format(latmin, latmax))

    band = dataset.read(1)
    print(band)
    print("Band Type= "+band.dtype.name)
    min = np.nanmin(band)
    max = np.nanmax(band)
    print("Min={:.3f}, Max={:.3f}".format(min,max))

    plt.imshow(band)
    plt.show()


def analyse_geotiff_pic(path_to_tif):
    '''Another quick script to analyse satellite data - this time for a RGB picture aka a 3-band tif file'''
    dataset = rs.open(path_to_tif)
    print("Size is {} x {} x {}".format(dataset.width,
                                        dataset.height,
                                        dataset.count))
    print("Extent Lon - left: {}, right: {} ".format(dataset.bounds.left,
                                           dataset.bounds.right))
    print("Extent Lat - bottom: {}, top: {} ".format(dataset.bounds.bottom,
                                           dataset.bounds.top))
    print("Projection: ", dataset.crs)

    red = dataset.read(1)
    green = dataset.read(2)
    blue = dataset.read(3)
    array = np.dstack((red, green, blue))

    plt.imshow(array)
    plt.show()


if __name__ == "__main__":
    path = "Aristarchus_IMP/"
    analyse_geotiff_1band(path+"height_slope_rockabundance.tif")