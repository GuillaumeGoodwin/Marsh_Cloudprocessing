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
def unzip_files (dir_list):
    """
    This function looks into the given directory list and checks:
    - whether there are compressed files
    - what the compression extensions are
    Then it uncompresses any compressed file it finds.
    Accepts .zip, .tar.gz and .7z

    args:
    - basedir (String): the base directory

    Returns:
    -Nothing. The uncompressed files will appear in the directory
    """


    """# To merge files
    for mypath in directory_list:
        myfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
        to_open = ""
        for file in myfiles:
            if file[-4:] == In_ext:"""


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
        dir = longdir.replace(basedir, "")
        files = [f for f in listdir(dir) if isfile(join(dir, f))]
        if len(files) > 0:
            for this_file in files:
                #if it's zipped, unzip it. It should be zipped because no unzipped clouds should remain. They're way too heavy.
                if this_file[-4:] == '.zip':
                    print dir + this_file
                    os.system('unzip ' + dir + this_file + ' -d ' + dir )
                    #Look at all the PC files of the chosen extension
                    cloud_files = [f for f in listdir(dir) if isfile(join(dir, f))]
                    #print cloud_files


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
                        #if i>3:
                            #break
                    os.system('cloudcompare.CloudCompare ' + to_open + '-NO_TIMESTAMP -MERGE_CLOUDS')


                    #

                    #print to_open
                            #

                            #print dir + cloud_file
                            #to_open = to_open + "-O " + dir + cloud_file[-4:] + '.las' + " "
                    #os.system('cloudcompare.CloudCompare ' + to_open + '-NO_TIMESTAMP -MERGE_CLOUDS')

                    s.system('rm '+dir+'*.las')
                    quit()


            """to_open = ""
            for file in myfiles:
                if file[-4:] == In_ext:
                    print mypath + file
                    to_open = to_open + "-O " + file + " "
            os.system('cloudcompare.CloudCompare ' + to_open + '-NO_TIMESTAMP -MERGE_CLOUDS')"""

        #quit()




################################################################################
def rasterize_cloud (basedir, In_name, Out_name, GRID_STEP, Fill_empty = 'INTERP'):
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
    - Fill_empty = 'INTERP': interpolate the elevation between points if a gird cell is void. Other options are available, but I'm not implementing them here for now.


    Returns:
    -Nothing. The uncompressed files will appear in the directory
    """



# Usage options
Base_dir = "/home/willgoodwin/Data/Venice_LiDAR/txt/"

In_ext = ".txt" # .laz, .las

GRID_STEP = 200



################################################################################
# The actual code
basedir = '/home/willgoodwin/Data/LiDAR/'

#This is where you find all the directories
directory_list = list_all_directories (basedir, [])

# This is where you merge the clouds
merge_clouds(basedir, directory_list, '.laz', 'A')

print 'booo'

quit()










directory_list = list()
for root, dirs, files in os.walk(Base_dir, topdown=False):
    for name in dirs:
        directory_list.append(name+'/')

if len(directory_list) == 0:
    directory_list.append(Base_dir)
print directory_list

# To merge files
for mypath in directory_list:
    myfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]
    to_open = ""
    for file in myfiles:
        if file[-4:] == In_ext:
            print mypath + file
            to_open = to_open + "-O " + file + " "
    os.system('cloudcompare.CloudCompare ' + to_open + '-NO_TIMESTAMP -MERGE_CLOUDS')

    # To make them into rasters
    for file in myfiles:
        if file[-4:] == ".bin":
            print mypath + file
            os.system('cloudcompare.CloudCompare -O ' + file + ' -NO_TIMESTAMP -RASTERIZE -GRID_STEP '+ str(GRID_STEP) + ' -PROJ MIN -SF_PROJ AVG -EMPTY_FILL CUSTOM_H -CUSTOM_HEIGHT -9999 -OUTPUT_RASTER_Z &')




        #print (LAZfile)
        #os.system('laszip -i ' + LAZfile + ' -o ' + LASfile)






quit()
