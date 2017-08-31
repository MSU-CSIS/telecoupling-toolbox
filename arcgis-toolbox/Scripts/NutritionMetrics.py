# Created on 2017-8-31
# Usage: Lower Limit of Energy Requirements (LLER) for area of interest.
#--------------------------------------------------------------------------------------------------------------

#Import all necessary module dependencies
import arcpy
import numpy
import os

arcpy.env.overwriteOutput = True

def nutritionMetrics(AOI, year, stature, outRaster):
	#This is the path to the mosaic database with demographic information
	mosaicDB = "C:\\Users\\Paul McCord\\Documents\\ArcGIS\\scratch\\scratchGDB.gdb\\World_Pop_Population_1km"

	#Create intermediate folder where output will be temporarily saved
	arcpy.CreateFolder_management(arcpy.env.scratchFolder, "intOutput")
	arcpy.AddMessage("foldercreated")
	os.chdir(os.path.join(arcpy.env.scratchFolder, "intOutput"))
	arcpy.AddMessage("made it here")
	
	#Testing to see how a clip would work
	arcpy.ExportMosaicDatasetItems_management(mosaicDB, os.path.join(arcpy.env.scratchFolder, "intOutput"), "ageGroup_" + year + "_", "", "", "", "FEATURE_CLASS", AOI)




if __name__ == '__main__':
	#Get the values of the input parameters
	AOI = arcpy.GetParameterAsText(0)
	year = arcpy.GetParameterAsText(1)
	stature = arcpy.GetParameterAsText(2)
	outRaster = arcpy.GetParameterAsText(3)
	
	#Run the Nutrition Metrics tool
	try:
		nutritionMetrics(AOI, year, stature, outRaster)
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))