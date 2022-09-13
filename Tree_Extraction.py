##################################################################################
# Purpose   :   Extract Tree Events's centroid points from LAS
# Author    :   Edward Wong
#
# Created   :   18/03/21
# Modified  :   22/07/21  
# Copyright :   (c) Eagle Technology Group 2022
# Copyright :   (c) Esri 2022

##################################################################################


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

    _zone_las = f"{filePath}\{zone}.las"
    dem_tin_tif = arcpy.Raster(f"{filePath}\{zone}.tin.tif")
    workspace = f"{myWorkspace}\{zone}_"
    desc = arcpy.Describe(f"{filePath}\{zone}.las")

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

    # Define the referenced variable
    _zone_Multipoint = f"{workspace}Multipoint"
    _zone_Singlepoint = f"{workspace}Singlepoint"
    _zone_Cluster = f"{workspace}Cluster"
    _zone_ClusterAll = f"{workspace}ClusterAll"
    _zone_ClusterNoise = f"{workspace}ClusterNoise"
    _zone_LasRaster = f"{workspace}LasRaster"

    # temp feature
    treeEvents = "TreeEvents"
    lasData = "lasData"

    # End Result
    _zone_TreeEvents = f"{zone}_{treeEvents}"
    _zone_TreesPoint = f"{zone}_Trees_Point"

    arcpy.ddd.LASToMultipoint(_zone_las, _zone_Multipoint, 0.5, [5], "ANY_RETURNS", None, 'PROJCS["NZGD_2000_New_Zealand_Transverse_Mercator",GEOGCS["GCS_NZGD_2000",DATUM["D_NZGD_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",1600000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",173.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]', "las", 1, "NO_RECURSION")
    arcpy.ddd.AddZInformation(_zone_Multipoint, "Z_MIN;Z_MAX;Z_MEAN;POINT_COUNT", '')
    arcpy.management.MultipartToSinglepart(_zone_Multipoint, _zone_Singlepoint)
    arcpy.stats.DensityBasedClustering(_zone_Singlepoint, _zone_Cluster, "DBSCAN", 10, "7 Meters", None, None, None)
    arcpy.ddd.AddZInformation(_zone_Cluster, "Z", '')


    # # Repeat for Color ID (-1 : 8 | [-1]) && != 0

    # Get the cluster and enrich the attributes 
    _zone_ClusterAll_Select, Count_one = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=_zone_Cluster, selection_type="NEW_SELECTION", where_clause="COLOR_ID = -1", invert_where_clause="INVERT")
    print(Count_one, "tree count")
    arcpy.cartography.AggregatePoints(_zone_ClusterAll_Select, _zone_ClusterAll, "2 Meters")
    arcpy.ddd.AddZInformation(_zone_ClusterAll , "Z_MIN;Z_MAX;Z_MEAN;LENGTH_3D;MIN_SLOPE;MAX_SLOPE;AVG_SLOPE;VERTEX_COUNT", '')


    # Get the tree noise for optional further process | Classify noise before the process
    _zone_ClusterNoise_Select, Count_two = arcpy.management.SelectLayerByAttribute(
    in_layer_or_view=_zone_Cluster, selection_type="NEW_SELECTION", where_clause="COLOR_ID = -1")
    print(Count_two, "noise count")
    arcpy.cartography.AggregatePoints(_zone_ClusterNoise_Select, _zone_ClusterNoise, "2 Meters")
    arcpy.ddd.AddZInformation(_zone_ClusterNoise, "Z_MIN;Z_MAX;Z_MEAN;LENGTH_3D;MIN_SLOPE;MAX_SLOPE;AVG_SLOPE;VERTEX_COUNT", '')

    
    # Enrich cluster to generate EventPoint
    arcpy.management.AddGeometryAttributes(_zone_ClusterAll, "CENTROID_INSIDE", "METERS", "SQUARE_METERS", 'PROJCS["NZGD_2000_New_Zealand_Transverse_Mercator",GEOGCS["GCS_NZGD_2000",DATUM["D_NZGD_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",1600000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",173.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]')
    arcpy.management.MakeXYEventLayer(_zone_ClusterAll, "INSIDE_X", "INSIDE_Y", treeEvents, 'PROJCS["NZGD_2000_New_Zealand_Transverse_Mercator",GEOGCS["GCS_NZGD_2000",DATUM["D_NZGD_2000",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",1600000.0],PARAMETER["False_Northing",10000000.0],PARAMETER["Central_Meridian",173.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]];-4020900 1900 10000;-100000 10000;-100000 10000;0.001;0.001;0.001;IsHighPrecision', "INSIDE_Z")
    arcpy.FeatureClassToFeatureClass_conversion(treeEvents, f"{myWorkspace}", _zone_TreeEvents)

    # Generate DTM
    arcpy.management.MakeLasDatasetLayer(_zone_las, lasData, "2", "'Last Return';'Single Return';'First of Many';'Last of Many';1;2;3;4;5;6;7;8;9;10;11;12;13;14;15", "INCLUDE_UNFLAGGED", "INCLUDE_SYNTHETIC", "INCLUDE_KEYPOINT", "EXCLUDE_WITHHELD", None, "INCLUDE_OVERLAP")
    arcpy.conversion.LasDatasetToRaster(lasData, _zone_LasRaster, "ELEVATION", "BINNING MAXIMUM LINEAR", "FLOAT", "CELLSIZE", 1, 1)

    # Add DSM from previous process
    arcpy.sa.AddSurfaceInformation(_zone_TreeEvents, _zone_LasRaster, "Z", "BILINEAR", 1, 1, 0, '')

    # Get CHM
    arcpy.management.CalculateField(_zone_TreeEvents, "Height", "!Z_Max! - !Z!", "PYTHON3", '', "TEXT", "NO_ENFORCE_DOMAINS")

    # Output the result
    arcpy.conversion.FeatureClassToFeatureClass(_zone_TreeEvents, f"{myWorkspace}", _zone_TreesPoint, '', 'Z_Min "Z_Min" true true false 8 Double 0 0,First,#,Trees_Event,Z_Min,-1,-1;Z_Max "Z_Max" true true false 8 Double 0 0,First,#,Trees_Event,Z_Max,-1,-1;Z_Mean "Z_Mean" true true false 8 Double 0 0,First,#,Trees_Event,Z_Mean,-1,-1;Length3D "Length3D" true true false 8 Double 0 0,First,#,Trees_Event,Length3D,-1,-1;Min_Slope "Min_Slope" true true false 8 Double 0 0,First,#,Trees_Event,Min_Slope,-1,-1;Max_Slope "Max_Slope" true true false 8 Double 0 0,First,#,Trees_Event,Max_Slope,-1,-1;Avg_Slope "Avg_Slope" true true false 8 Double 0 0,First,#,Trees_Event,Avg_Slope,-1,-1;Vertex_Cnt "Vertex_Cnt" true true false 4 Long 0 0,First,#,Trees_Event,Vertex_Cnt,-1,-1;Shape_Length "Shape_Length" false true true 8 Double 0 0,First,#,Trees_Event,Shape_Length,-1,-1;Shape_Area "Shape_Area" false true true 8 Double 0 0,First,#,Trees_Event,Shape_Area,-1,-1;INSIDE_X "INSIDE_X" true true false 8 Double 0 0,First,#,Trees_Event,INSIDE_X,-1,-1;INSIDE_Y "INSIDE_Y" true true false 8 Double 0 0,First,#,Trees_Event,INSIDE_Y,-1,-1;INSIDE_Z "INSIDE_Z" true true false 8 Double 0 0,First,#,Trees_Event,INSIDE_Z,-1,-1;Z "Z" true true false 8 Double 0 0,First,#,Trees_Event,Z,-1,-1;Height "Height" true true false 4 Float 0 0,First,#,Trees_Event,Height,-1,-1', '')


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
    myWorkspace = r"C:\Users\exw\Documents\ArcGIS\Projects\Tree_Module_Code2\Tree_Module_Code2.gdb"
    myFilePath = r"C:\Users\exw\Desktop\NZEUC2022\TePaeLAS"
    with arcpy.EnvManager(scratchWorkspace=myWorkspace, workspace=myWorkspace):
        LAS_Trees_Extraction(myWorkspace, myFilePath, "tepae", False)
