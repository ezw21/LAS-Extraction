# Segmenting harvestable areas within managed_area=5, considering restrictions around streams and wildlife
# Author:      Edward Wong
# Created:     11/03/202
import arcpy

# Segment lease_5
bla, count = arcpy.management.SelectLayerByAttribute(
    "Leases", "NEW_SELECTION", "OBJECTID = 5", None)
arcpy.CopyFeatures_management("Leases", 'Lease_Area_5')
# Buff goshawk_Nest
arcpy.analysis.Buffer("Goshawk_Nests", r"C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\Goshawk_Nests_Buff_800m",
                      "800 Meters", "FULL", "ROUND", "NONE", None, "PLANAR")
bla_2, count = arcpy.management.SelectLayerByAttribute(
    "Streams", "NEW_SELECTION", "HasSpawning = 'Yes'", None)
# Buff FishSpawn
arcpy.analysis.Buffer(bla_2, r"C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\Fish_Spwam_Buff_100m",
                      "100 Meters", "FULL", "ROUND", "NONE", None, "PLANAR")
bla_3, count = arcpy.management.SelectLayerByAttribute(
    "Streams", "NEW_SELECTION", "HasSpawning = 'No'", None)
# Buff FishNoSpawn
arcpy.analysis.Buffer(bla_3, r"C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\Fish_Spwam_Buff_50m",
                      "50 Meters", "FULL", "ROUND", "NONE", None, "PLANAR")
bla_3 = arcpy.management.SelectLayerByLocation(
    "Fish_Spwam_Buff_50m;Fish_Spwam_Buff_100m;Goshawk_Nests_Buff_800m", "INTERSECT", "Lease_Area_5", None, "NEW_SELECTION", "INVERT")

# Press the delete button manually to removed unncessary feature then run the codes below
input("Press delete and accept manually")

arcpy.analysis.Clip("Goshawk_Nests_Buff_800m", "Lease_Area_5",
                    r"C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\Lease_Area_5_Clip_Lease_Nest800", None)
arcpy.analysis.Clip("Fish_Spwam_Buff_100m", "Lease_Area_5",
                    r"C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\Lease_Area_5_Clip_Lease_Fish100", None)
arcpy.analysis.Clip("Fish_Spwam_Buff_50m", "Lease_Area_5",
                    r"C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\Lease_Area_5_Clip_Lease_Fish50", None)
