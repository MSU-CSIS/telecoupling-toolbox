# Created on 2017-8-31
# Usage: Lower Limit of Energy Requirements (LLER) for area of interest.
#--------------------------------------------------------------------------------------------------------------

#Import all necessary module dependencies
import arcpy
import numpy
import os
import re

arcpy.env.overwriteOutput = True

def nutritionMetrics(AOI, year, stature, outRaster):
	#This is the path to the mosaic database with demographic information
	mosaicDB = "Z:\\Francesco Tonini\\Telecoupling\\Data\\TelecouplingDB.gdb\\test_age_structure_worldpop"

	#Create intermediate folder where output will be temporarily saved
	arcpy.CreateFolder_management(arcpy.env.scratchFolder, "intOutput")
	arcpy.AddMessage("foldercreated")
	os.chdir(os.path.join(arcpy.env.scratchFolder, "intOutput"))
	arcpy.AddMessage("made it here")
	
	#Export only images consistent with the Year and Area of Interest
	query = "Year = " + year
	basename = "ageStructure_" 
	arcpy.ExportMosaicDatasetItems_management(mosaicDB, os.path.join(arcpy.env.scratchFolder, "intOutput"), basename, query, "", "", "FEATURE_CLASS", AOI)
	
	#Loop through the exported rasters and calculate nutrition metrics for each rasters
	rasterList = []
	for file in os.listdir(os.path.join(arcpy.env.scratchFolder, "intOutput")):
		if file.endswith(".TIF"):
			rasterList.append(file)
	arcpy.AddMessage(rasterList)
	
	#Calculate nutrition metrics
	LLER = 0    #This will keep the tally of 'Lower Limit of Energy Requirement' in kcal/day for the study area.
	regex = re.compile(r'\d+')
	statureInt = int(stature)
	for r in rasterList:
		OID = regex.findall(r)[0]
		
		#The appropriate equation is added to each age group and a running tally of LLER is kept.
		#The female 00-04 age group
		if OID in ["1", "2", "3", "4", "5"]:
			height = (statureInt / 161.8) * 84.97556    #note that 2014 heights for Americans are used to standardized height values
			arcpy.AddMessage("height is " + str(height))
			kg50 = 15.5 * ((height / 100)**2)
			arcpy.AddMessage("kg50 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population is " + str(pop))
			f0004 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (6.3 * 2)) * pop
			arcpy.AddMessage("LLER for f0004 age group(total kcal/day): " + str(f0004))
			LLER += f0004
		
		#The male 00-04 age group
		elif OID in ["6", "7", "8", "9", "10"]:
			m0004 = 160000000    #remove this tomorrow
			LLER += m0004
			arcpy.AddMessage("LLER for males and females in the 0004 age group (total kcal/day): " + str(LLER))
			
		else:
			arcpy.AddMessage("False")
	
	
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