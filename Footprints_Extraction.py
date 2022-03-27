# Extract building footprint from LAS.
# Author:      Edward Wong
# Created:     23/02/2022
import arcpy
import time
import math
import datetime


def LAS_Footprints_Extraction(myWorkspace, filePath, zone, noise):  # Model
    start = time.time()
    print(datetime.datetime.now())
    print("Extracting 3D building and footprint..\n")

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

    if (noise):
        print(datetime.datetime.now())
        _zone_Noise = f"{workspace}Noise"
        arcpy.ddd.ClassifyLasNoise(_zone_las, method='ISOLATION', edit_las='CLASSIFY',
                                   withheld='NO_WITHHELD', ground=Dem_tin_tif,
                                   compute_stats='COMPUTE_STATS',
                                   low_z='2 Meters', high_z='',
                                   max_neighbors=10, step_width='8 Meters',
                                   step_height='8 Meters', out_feature_class=_zone_Noise,
                                   update_pyramid='UPDATE_PYRAMID')
        print("Classified LAS Noise")

        # Classify overlap points
        arcpy.ddd.ClassifyLasOverlap(
            _zone_las, "0.624 Meters", "DEFAULT", "PROCESS_EXTENT", "COMPUTE_STATS", "UPDATE_PYRAMID")
        print("Classified overlap points")

#     arcpy.ddd.ChangeLasClassCodes(_zone_las, "0 2 SET SET SET SET;1 2 SET SET SET SET;3 2 SET SET SET SET;4 2 SET SET SET SET;5 2 SET SET SET SET;7 2 SET SET SET SET;18 2 SET SET SET SET;",
#                                   "COMPUTE_STATS", "DEFAULT", None,
#                                   "PROCESS_EXTENT", "UPDATE_PYRAMID")
#     print("Changed LAS ClassCode")

    print(datetime.datetime.now())
    # Filter LAS to Class_6
    arcpy.management.MakeLasDatasetLayer(
        _zone_las, _zone_las, class_code=[6])

    # Process: LAS Point Statistics As Raster (LAS Point Statistics As Raster) (management)
    _zone_Raster = f"{workspace}Raster"
    arcpy.management.LasPointStatsAsRaster(in_las_dataset=_zone_las, out_raster=_zone_Raster,
                                           method="PREDOMINANT_CLASS", sampling_type="CELLSIZE", sampling_value=0.5)
    _zone_Raster = arcpy.Raster(_zone_Raster)

    # Process: Raster to Polygon (Raster to Polygon) (conversion)
    _zone_Polygon = f"{workspace}BuildingRaw"
    with arcpy.EnvManager(outputMFlag="Disabled", outputZFlag="Disabled"):
        arcpy.conversion.RasterToPolygon(in_raster=_zone_Raster, out_polygon_features=_zone_Polygon, simplify="NO_SIMPLIFY",
                                         raster_field="Value", create_multipart_features="SINGLE_OUTER_PART", max_vertices_per_feature=None)
    _zone_PolygonSmooth = f"{workspace}BuildingSmooth"
    arcpy.cartography.SmoothPolygon(_zone_Polygon, _zone_PolygonSmooth,
                                    "PAEK", "5 Meters", "FIXED_ENDPOINT", "RESOLVE_ERRORS", None)

    # Low Dense
    _zone_LowDensePolygon, Count_one = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=_zone_PolygonSmooth, selection_type="NEW_SELECTION", where_clause="Shape_Length > (Shape_Area * 1.05) And Shape_Area > 15", invert_where_clause="")
    print(Count_one)

    _zone_LowDensePolygonAggr = f"{workspace}BuildingJoin"
    arcpy.cartography.AggregatePolygons(_zone_LowDensePolygon, _zone_LowDensePolygonAggr,
                                        "0.51 Meters", "10 SquareMeters", "10 SquareMeters", "ORTHOGONAL")

    _zone_DensePolygon = f"{workspace}DensePolygon"
    arcpy.cartography.SimplifyBuilding(_zone_LowDensePolygonAggr, _zone_DensePolygon,
                                       "1 Meters", "0 SquareMeters", "NO_CHECK", None, "NO_KEEP")

    # Process: Eliminate Polygon Part (Eliminate Polygon Part) (management)
    _zone_DensePolygonClean = f"{workspace}DenseBuildingClean"
    arcpy.management.EliminatePolygonPart(in_features=_zone_DensePolygon, out_feature_class=_zone_DensePolygonClean,
                                          condition="AREA", part_area="10 SquareMeters", part_area_percent=0, part_option="CONTAINED_ONLY")

    # High Dense

    # Process: Select Layer By Attribute (Select Layer By Attribute) (management)
    _zone_HighDensePolygon, Count_two = arcpy.management.SelectLayerByAttribute(
        in_layer_or_view=_zone_PolygonSmooth, selection_type="NEW_SELECTION", where_clause="Shape_Length < (Shape_Area * 1.05) And Shape_Area > 15", invert_where_clause="")
    print(Count_two)

    _zone_HighDensePolygonSimp = f"{workspace}HighDensePolygon"
    arcpy.cartography.SimplifyBuilding(_zone_HighDensePolygon, _zone_HighDensePolygonSimp,
                                       "1 Meters", "0 SquareMeters", "NO_CHECK", None, "NO_KEEP")

    # Process: Eliminate Polygon Part (Eliminate Polygon Part) (management)
    _zone_HighDensePolygonClean = f"{workspace}HighDenseBuildingClean"
    arcpy.management.EliminatePolygonPart(in_features=_zone_HighDensePolygonSimp, out_feature_class=_zone_HighDensePolygonClean,
                                          condition="AREA", part_area="10 SquareMeters", part_area_percent=0, part_option="CONTAINED_ONLY")

    _zone_PolygonClean = f"{workspace}BuildingClean"
    arcpy.Merge_management([_zone_DensePolygonClean, _zone_HighDensePolygonClean],
                           _zone_PolygonClean, "", "ADD_SOURCE_INFO")

    # Process: Regularize Building Footprint (Regularize Building Footprint) (3d)
    _zone_Footprints = f"{workspace}Footprints"
    arcpy.ddd.RegularizeBuildingFootprint(in_features=_zone_PolygonClean, out_feature_class=_zone_Footprints, method="RIGHT_ANGLES", tolerance=1, densification=1,
                                          precision=0.15, diagonal_penalty=1.5, min_radius=0.1, max_radius=1000000, alignment_feature="", alignment_tolerance="", tolerance_type="DISTANCE")

    print(datetime.datetime.now())
    # Process: LAS Building Multipatch (LAS Building Multipatch) (3d)
    _zone_3D = (workspace + "3D")
    arcpy.ddd.LasBuildingMultipatch(in_las_dataset=_zone_las, in_features=_zone_Footprints, ground=Dem_tin_tif,
                                    out_feature_class=_zone_3D, point_selection="BUILDING_CLASSIFIED_POINTS", simplification="0.1 Meters")

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
        LAS_Footprints_Extraction(myWorkspace, myFilePath, "LAS_FILE", False)
