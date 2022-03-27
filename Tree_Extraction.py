# Extract Tree centroid points from LAS
# Author:      Edward Wong
# Created:     18/03/2022
import arcpy
import time
import math
import datetime


def LAS_Trees_Extraction(myWorkspace, filePath, zone, noise):  # Model
    start = time.time()
    print(datetime.datetime.now())
    print("Extracting 3D Trees..\n")

    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    # Check out any necessary licenses.
    arcpy.CheckOutExtension("3D")

    _zone_las = f"{zone}.las"
    Dem_tin_tif = arcpy.Raster(f"{zone}.tin.tif")
    workspace = f"{myWorkspace}\{zone}_"
    desc = arcpy.Describe(f"{filePath}")

    if desc.usesRelativePath:
        pathType = 'Relative'
    else:
        pathType = 'Absolute'

    # Determine state of statistics
    if desc.needsUpdateStatistics:
        if desc.hasStatistics:
            statistics = 'Out-of-date'
        else:
            statistics = 'Missing'
    else:
        statistics = 'Current'

    print("LAS Dataset Name: \t\t{0}.las\n"
          "Point Count: \t\t\t{1}\n"
          "Surface Constraint Count: \t{2}\n"
          "Path Type: \t\t\t{3}\n"
          "Statistics Status: \t\t{4}"
          .format(desc.basename, desc.pointCount,
                  desc.constraintCount, pathType,
                  statistics))
    print("\nSTART")

# HEREEEEEEEEEEEEEEEE




# Display total time consumption
    minute = 0
    seconds = (time.time() - start)
    while (seconds >= 60):
        seconds -= 60
        minute += 1
    print("Total time consumption = {}(m) {}(s)".format(
        minute, math.ceil(seconds)))


if __name__ == '__main__':
    # Global Environment settings
    myWorkspace = r"C:\Users\exw\Documents\ArcGIS\Projects\PROJECT\PROJECT.gdb"
    myFilePath = r"C:\PHYSICAL_PATH\LAS_File.las"
    with arcpy.EnvManager(scratchWorkspace=myWorkspace, workspace=myWorkspace):
        LAS_Trees_Extraction(myWorkspace, myFilePath, "LAS_FILE", False)
