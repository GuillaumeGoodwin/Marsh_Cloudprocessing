"""
Process_Clouds.py

This file takes the files in a directory (or more) and processes all the bazillions of point clouds.
Hopefully it will get to the stage where:

- you can select several folders and operate on many clouds
- you can choose the input format (.txt, .las, .laz)
- you can merge the clouds of a given format (or all formats) in a given folder
- you can rasterize the resulting big cloud and make it into a .tiff


This uses CloudCompare in the command line. Dowload CloudCompare here: http://cloudcompare.org/release/index.html

Make this a function/module?


This works in the LASTools environment

"""

################################################################################
# Useful Python packages
#import matplotlib
#matplotlib.use('Agg')

import os
import sys
import numpy as np
from os import listdir
from os.path import isfile, join


################################################################################
import numpy as np
import functools
import math as mt
import cmath
import scipy as sp
import scipy.stats as stats
from datetime import datetime
import cPickle
from pylab import *
import functools
import itertools as itt
from osgeo import gdal, osr
from osgeo import gdal, gdalconst
from osgeo.gdalconst import *
from copy import copy
from matplotlib import cm
import matplotlib.colors as colors
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.ticker as tk
from matplotlib import rcParams
from mpl_toolkits.axes_grid1.inset_locator import *
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FormatStrFormatter
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.basemap import Basemap, cm
from matplotlib.patches import Rectangle
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
import timeit



import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

################################################################################

################################################################################
def list_all_directories (directory, dir_list):
    """
    This function looks into a directory and checks:
    - whether there are subdirectories
    - what these subdirectories are

    args:
    - basedir (String): the directory

    Returns:
    - dir_list (List): a list of the directories in the base directory, in order of finding

    NB: this is a recursive function

    """

    for root, dirs, files in os.walk(directory, topdown=True):
        if len(dirs) > 0:
            keep_going = True
            for dir in dirs:
                full_dir =  directory + dir + '/'
                if os.path.isdir(full_dir):
                    dir_list.append(full_dir)
                    list_all_directories(full_dir, dir_list)
        else:
            keep_going = False

    return dir_list




################################################################################
def merge_clouds (basedir, dir_list, In_ext, Out_name, delete_clouds = True):
    """
    This function looks into a base directory and checks:
    - whether there are subdirectories
    - whether there are clouds of the given extension
    Then it opens all the clouds with CloudCompare's command line mode and merges them.
    Accepts .txt, .laz, .las, .bin
    It will also delete all the unmerged clouds once it is done, to save space.
    Finally, it renames the merged cloud.
    NB: You have to click OK at the end of the merge.

    args:
    - dir_list (List of Strings): the base directory
    - In_ext (String): the cloud file extension
    - Out_name (String): The output cloud name (includes directory, no extension)

    Returns:
    -Nothing. The merged file will appear in the directory
    """

    #Open a directory
    for longdir in dir_list:
        dir = longdir.replace(basedir, "UK/SLW_NP/2017/")
        #dir = longdir.replace(basedir, "")
        files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if len(files) > 0:
            for this_file in files:
                #if it's zipped, unzip it. It should be zipped because no unzipped clouds should remain. They're way too heavy.
                if this_file[-4:] == '.zip':
                    print dir + this_file
                    os.system('unzip ' + dir + this_file + ' -d ' + dir )
                    #Look at all the PC files of the chosen extension
                    cloud_files = [f for f in listdir(dir) if isfile(join(dir, f))]

                    i = 0
                    for cloud_file in cloud_files:
                        if cloud_file[-4:] == In_ext:
                            os.system('laszip -i ' + dir+cloud_file + ' -o ' + dir + str(i) + '.las')
                            os.system('rm ' + dir + cloud_file)
                        i+=1

                    to_open = ""
                    las_files = [f for f in listdir(dir) if isfile(join(dir, f))]

                    i = 0
                    for las_file in las_files:
                        print las_file
                        if las_file[-4:] == '.las':
                            if las_file != ".laz.las":
                                to_open = to_open + "-O " + dir + las_file + " "
                        i+=1

                    os.system('cloudcompare.CloudCompare ' + to_open + '-NO_TIMESTAMP -MERGE_CLOUDS')
                    os.system('rm '+dir+'*.las &')

                    quit()






################################################################################
def rasterize_clouds (basedir, dir_list, GRID_STEP, zipped = False, Fill_empty = 'INTERP'):
    """
    This function looks into a base directory and checks:
    - whether there are subdirectories
    - whether the input clouds are present in the directory
    Then it rasterizes it.
    Accepts only .bin for now
    IMPORTANT: If you don't want it to rasterize a whole bunch of unwanted clouds, make sure you delete them beforehand.

    args:
    - basedir (String): the base directory
    - In_name (List of Strings): The list of names of the clouds to rasterize. No extension
    - Out_name (String): The list of names for the outputs. No extension
    - GRID_STEP (Int): the grid step of the raster. Must be in the same units as the input cloud
    - Fill_empty = 'INTERP': interpolate the elevation between points if a grid cell is void. Other options are available, but I'm not implementing them here for now.


    Returns:
    -Nothing. The rasterized files will appear in the directory
    """

    #Open a directory
    for longdir in dir_list:
        dir = longdir.replace(basedir, "UK/SLW_NP/2017/")
        #dir = longdir.replace(basedir, "")
        files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if len(files) > 0:
            for this_file in files:

                if zipped == True:
                    extension = '.las'
                    if this_file[-4:] == '.zip':
                        print dir + this_file
                        os.system('unzip ' + dir + this_file + ' -d ' + dir )
                        #Look at all the PC files of the chosen extension
                        cloud_files = [f for f in listdir(dir) if isfile(join(dir, f))]
                        i = 0
                        for cloud_file in cloud_files:
                            if cloud_file[-4:] == '.laz':
                                os.system('laszip -i ' + dir+cloud_file + ' -o ' + dir + str(i) + '.las')
                                os.system('rm ' + dir + cloud_file)
                            i+=1

                else:
                    extension = '.bin'


        files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if len(files) > 0:
            for this_file in files:
                if this_file[-4:] == extension:
                    if this_file != '.laz_MERGED.bin':
                        print dir + this_file
                        os.system('cloudcompare.CloudCompare -O ' + dir+this_file + ' -NO_TIMESTAMP -RASTERIZE -GRID_STEP '+ str(GRID_STEP) + ' -PROJ MIN -SF_PROJ AVG -EMPTY_FILL ' + Fill_empty + ' -OUTPUT_RASTER_Z')                        #os.system('cloudcompare.CloudCompare -O ' + dir+this_file + ' -NO_TIMESTAMP -RASTERIZE -GRID_STEP '+ str(GRID_STEP) + ' -PROJ MIN -SF_PROJ AVG -EMPTY_FILL CUSTOM_H -CUSTOM_HEIGHT -9999 -OUTPUT_RASTER_Z &')


################################################################################
def merge_tiffs (basedir, dir_list, cutdir, Out_name):

    """
    This function looks into a base directory and checks:
    - whether there are subdirectories
    - whether the input clouds are present in the directory
    Then it rasterizes it.
    Accepts only .bin for now
    IMPORTANT: If you don't want it to rasterize a whole bunch of unwanted clouds, make sure you delete them beforehand.

    args:
    - basedir (String): the base directory
    - In_name (List of Strings): The list of names of the clouds to rasterize. No extension
    - Out_name (String): The list of names for the outputs. No extension
    - GRID_STEP (Int): the grid step of the raster. Must be in the same units as the input cloud
    - Fill_empty = 'INTERP': interpolate the elevation between points if a grid cell is void. Other options are available, but I'm not implementing them here for now.


    Returns:
    -Nothing. The rasterized files will appear in the directory

    NB: operates in the LSDTT_TEST environment to have gdal
    """

    #Open a directory
    for longdir in dir_list:
        dir = longdir.replace(basedir, "UK/SLW_NP/2017/")
        #dir = longdir.replace(basedir, "")
        files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if len(files) > 0:
            to_open = ""
            tif_files = [f for f in listdir(dir) if isfile(join(dir, f))]
            for this_file in tif_files:
                if this_file[-4:] == '.tif':
                    if this_file != ".laz.las":
                        to_open = to_open + " " + dir + this_file + " "

                    #if this_file != '.laz_MERGED.tif':
                    print dir + this_file
            os.system('gdal_merge.py -of ENVI - -o ' + dir + 'out.tif ' + to_open)
            os.system('gdal_translate -b 1 -b 9 -of ENVI -a_srs EPSG:27700 ' + dir + 'out.tif '+ dir + Out_name +'.bil')
            os.system('gdalwarp -of ENVI -t_srs EPSG:27700 -cutline '+ cutdir + 'domain.shp -crop_to_cutline ' + dir + Out_name + '.bil '+ dir + Out_name +'_clip.bil')




################################################################################
import gdal

def ReadBilFile(directory, file, band):
    ds = gdal.Open(directory+file+".bil")
    data = np.array(ds.GetRasterBand(band).ReadAsArray())
    return data



################################################################################
def Simple_map(directory, arr, fig_name):


    fig=plt.figure(1, facecolor='White',figsize=[10,10])
    ax1 = plt.subplot2grid((1,1),(0,0),colspan=1, rowspan=1)

    # Name the axes
    ax1.set_xlabel('x (m)', fontsize = 12)
    ax1.set_ylabel('y (m)', fontsize = 12)

    # Make a mask!
    #Platform_mask = np.ma.masked_where(Platform <=0, Platform)
    #Platform_mask[Platform_mask>0] = DEM[Platform_mask>0]

    # Make a map!
    #Map_HS = ax1.imshow(HS, interpolation='None', cmap=plt.cm.gist_gray, vmin = 100, vmax = 200)
    Map_DEM = ax1.imshow(arr, interpolation='None', cmap=plt.cm.PiYG, vmin = -0.5, vmax = 0.5, alpha = 0.8)
    #Map_DEM = ax1.imshow(DEM, interpolation='None', cmap=plt.cm.gist_gray, vmin = np.amin(DEM[DEM!=Nodata_value]), vmax = np.amax(DEM), alpha = 0.5)
    #Map_Marsh = ax1.imshow(Platform_mask, interpolation='None', cmap=plt.cm.gist_earth, vmin=np.amin(DEM[DEM!=Nodata_value]), vmax=np.amax(DEM), alpha = 0.5)


    # create an axes on the right side of ax. The width of cax will be 5%
    # of ax and the padding between cax and ax will be fixed at 0.05 inch.
    divider = make_axes_locatable(ax1)
    cax = divider.append_axes("right", size="5%", pad=0.05)

    plt.colorbar(Map_DEM, cax=cax)

    plt.savefig(directory + fig_name + '.png')



################################################################################
# The actual code
#basedir = '/home/willgoodwin/Data/LiDAR/'
basedir = '/home/willgoodwin/Data/LiDAR/UK/SLW_NP/'
basedir1 = '/home/willgoodwin/Data/LiDAR/UK/SLW_NP/2009/'
basedir2 = '/home/willgoodwin/Data/LiDAR/UK/SLW_NP/2017/'
GRID_STEP = 1 # In the unit of the cloud

#This is where you find all the directories
#directory_list = list_all_directories (basedir, [])
directory_list = ['/home/willgoodwin/Data/LiDAR/UK/SLW_NP/2009/']
print directory_list




# This is where you merge the clouds
#merge_clouds(basedir, directory_list, '.laz', 'A')

#rasterize_clouds (basedir, directory_list, GRID_STEP, zipped = True)


#merge_tiffs(basedir1, directory_list, basedir, 'Band_ZI')
#merge_tiffs(basedir2, directory_list, basedir, 'Band_ZI')

print 'booo'



Array_09 = ReadBilFile(basedir1, 'Band_ZI_clip', 1)
Array_17 = ReadBilFile(basedir2, 'Band_ZI_clip', 1)

#print Array1
#print Array2

Array_diff = - Array_09 + Array_17

#print Array3


Simple_map(basedir, Array_09, '1')
Simple_map(basedir, Array_17, '2')
Simple_map(basedir, Array_diff, '3')

"""SOMECLOUDS ARE SUPER HEAVY. mAKE SURE YOU ONLY LOAD Z TO MAKE IT LIGHTER"""

quit()
