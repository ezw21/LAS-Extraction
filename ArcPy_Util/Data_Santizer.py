""" 
    Author: Edward Wong
    DateCreated: 12/03/2022
    Purpose: Sanitize Bad data with desired pattern/value

    Update PATH & TARGETFIELD and run the code
"""
import arcpy


def sanitizeData():

    # The Literal Path of feat/ure class
    path = r'C:\Users\exw\Documents\ArcGIS\Projects\aaa\aaa.gdb\aaaaaaaaaaaaa'

    # COUNT       - Count of value that met if-condition
    # FIELDINDEX  - Index of target field in table
    # TARGETFIELD - Target field to be sanitized
    count = 0
    fieldIndex = 0
    targetField = "CRASH_FATAL_CNT"

    # Init empty list to store all fieldName(s)
    fieldNames = []
    for field in arcpy.ListFields(path):
        fieldNames.append(field.name)

    # Point cursor to the table's memory address in hex
    with arcpy.da.UpdateCursor(path, fieldNames) as cursor:
        print(cursor, type(cursor))

        # Filter the table and get targetField's index to not modified all field, logic can be alter accordingly
        for field in range(len(fieldNames)):
            if (fieldNames[field] == targetField):
                fieldIndex = field
        print("Target field : {} is on Index : {}".format(targetField, fieldIndex))

        for row in cursor:                          # Loop through each row of the attribute table
            rowU = row
            print(rowU[fieldIndex], "before")

            if(rowU[fieldIndex] == 0):              # Specify the condition to sanitize
                count += 1                          # Pattern of sanitizing - Incremental
                rowU[fieldIndex] = count
                print(rowU[fieldIndex], "after")
                # Update the cursor with the new value
                cursor.updateRow(rowU)

    del cursor                                      # Delete cursoe object


sanitizeData()
