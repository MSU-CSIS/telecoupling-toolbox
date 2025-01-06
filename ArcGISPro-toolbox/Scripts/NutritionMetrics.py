# Created on 2017-8-31
# Usage: Lower Limit of Energy Requirements (LLER) for area of interest.
#--------------------------------------------------------------------------------------------------------------

#Import all necessary module dependencies
import arcpy
from arcpy.sa import *
import numpy
import os
import string
import re
import shutil

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

#Set whether tool is licensed
def isLicensed():
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            raise Exception
    except:
        return False
    return True

def autoIncrement(pInterval = 1):
	global rec
	rec = rec + pInterval
	return rec

def nutritionMetrics(AOI, year, maleStature, femaleStature, rasterList):

	#Create intermediate folder where output will be temporarily saved
	arcpy.CreateFolder_management(arcpy.env.scratchFolder, "intOutput")
	#arcpy.AddMessage("scratch folder was created")
	os.chdir(os.path.join(arcpy.env.scratchFolder, "intOutput"))
	arcpy.AddMessage("Calculating nutrition metrics... ")
	
	#Return only rasters with the year selected by the user
	rasterYearList = []
	for r in rasterList:
		if year in r:
			rasterYearList.append(r)
	
	#Clip the continent raster by the AOI
	for r in rasterYearList:
		rasterName = r[:-4] + "_clip.img"
		outExtractByMask = ExtractByMask(r, AOI)
		outExtractByMask.save(os.path.join(arcpy.env.scratchFolder, "intOutput", rasterName))
	
	#Loop through the exported rasters and calculate nutrition metrics for each raster
	#Get a list of the clipped rasters
	arcpy.env.workspace = os.path.join(arcpy.env.scratchFolder, "intOutput")
	clippedRasterList = arcpy.ListRasters()
	
	#Calculate nutrition metrics
	LLER = 0    #This will keep the tally of 'Lower Limit of Energy Requirement' in kcal/day for the study area (AOI).
	totalPop = 0    #This will keep the tally of total population in the study area (AOI).
	groupList = []
	maleStatureInt = float(maleStature)
	femaleStatureInt = float(femaleStature)
	#arcpy.AddMessage(clippedRasterList)
	for r in clippedRasterList:
		
		#The appropriate equation is added to each age group and a running tally of LLER is kept.
		#The female 00-04 age group
		if "0004_F" in r:
			height = (femaleStatureInt / 161.8) * 84.97556    #note that 2014 heights for Americans are used to standardized height values (CDC, 2016)
			kg50 = 15.5 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf0004 = array.sum()
			nutf0004 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (6.3 * 2)) * popf0004
			LLER += nutf0004
			totalPop += popf0004
			sexAge = "0004_F"
			groupList.append(sexAge)
		
		#The male 00-04 age group
		elif "0004_M" in r:
			height = (maleStatureInt / 175.7) * 86.4522
			kg50 = 15.8 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm0004 = array.sum()
			nutm0004 = ((310.2 + 63.3 * kg50 - 0.263 * (kg50)**2) + (6.3 * 2)) * popm0004
			LLER += nutm0004
			totalPop += popm0004
			sexAge = "0004_M"
			groupList.append(sexAge)
		
		#The female 05-09 age group
		elif "0509_F" in r:
			height = (femaleStatureInt / 161.8) * 121.7617
			kg50 = 15.52 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf0509 = array.sum()
			nutf0509 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (8.22 * 2)) * popf0509
			LLER += nutf0509
			totalPop += popf0509
			sexAge = "0509_F"
			groupList.append(sexAge)
		
		#The male 05-09 age group
		elif "0509_M" in r:
			height = (maleStatureInt / 175.7) * 122.0305
			kg50 = 15.6 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm0509 = array.sum()
			nutm0509 = ((310.2 + 63.3 * kg50 - 0.263 * (kg50)**2) + (6.58 * 2)) * popm0509
			LLER += nutm0509
			totalPop += popm0509
			sexAge = "0509_M"
			groupList.append(sexAge)
		
		#The female 10-14 age group
		elif "1014_F" in r:
			height = (femaleStatureInt / 161.8) * 151.4866
			kg5 = 15.19 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf1014 = array.sum()
			nutf1014 = (0.85 * (263.4 + 65.3 * kg5 - 0.454 * (kg5)**2) + (9.86 * 2)) * popf1014
			LLER += nutf1014
			totalPop += popf1014
			sexAge = "1014_F"
			groupList.append(sexAge)
			
		#The male 10-14 age group
		elif "1014_M" in r:
			height = (maleStatureInt / 175.7) * 149.3088
			kg5 = 15.14 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm1014 = array.sum()
			nutm1014 = (0.85 * (310.2 + 63.3 * kg5 - 0.263 * (kg5)**2) + (10.41 * 2)) * popm1014
			LLER += nutm1014
			totalPop += popm1014
			sexAge = "1014_M"
			groupList.append(sexAge)
			
		#The female 15-19 age group
		elif "1519_F" in r:
			height = (femaleStatureInt / 161.8) * 163.1308
			kg5 = 17.19 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf1519 = array.sum()
			nutf1519 = (1.55 * (486.6 + 8.126 * kg5)) * popf1519
			LLER += nutf1519
			totalPop += popf1519
			sexAge = "1519_F"
			groupList.append(sexAge)
			
		#The male 15-19 age group
		elif "1519_M" in r:
			height = (maleStatureInt / 175.7) * 176.185
			kg5 = 18.10 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm1519 = array.sum()
			nutm1519 = (1.55 * (692.2 + 15.057 * kg5)) * popm1519
			LLER += nutm1519
			totalPop += popm1519
			sexAge = "1519_M"
			groupList.append(sexAge)
			
		#The female 20-24 age group
		elif "2024_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf2024 = array.sum()
			nutf2024 = (1.55 * (486.6 + 8.126 * kg5)) * popf2024
			LLER += nutf2024
			totalPop += popf2024
			sexAge = "2024_F"
			groupList.append(sexAge)
			
		#The male 20-24 age group
		elif "2024_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm2024 = array.sum()
			nutm2024 = (1.55 * (692.2 + 15.057 * kg5)) * popm2024
			LLER += nutm2024
			totalPop += popm2024
			sexAge = "2024_M"
			groupList.append(sexAge)
		
		#The female 25-29 age group
		elif "2529_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf2529 = array.sum()
			nutf2529 = (1.55 * (486.6 + 8.126 * kg5)) * popf2529
			LLER += nutf2529
			totalPop += popf2529
			sexAge = "2529_F"
			groupList.append(sexAge)
			
		#The male 25-29 age group 
		elif "2529_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm2529 = array.sum()
			nutm2529 = (1.55 * (692.2 + 15.057 * kg5)) * popm2529
			LLER += nutm2529
			totalPop += popm2529
			sexAge = "2529_M"
			groupList.append(sexAge)
			
		#The female 30-34 age group
		elif "3034_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf3034 = array.sum()
			nutf3034 = (1.55 * (845.6 + 8.118 * kg5)) * popf3034
			LLER += nutf3034
			totalPop += popf3034
			sexAge = "3034_F"
			groupList.append(sexAge)
			
		#The male 30-34 age group
		elif "3034_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm3034 = array.sum()
			nutm3034 = (1.55 * (873.1 + 11.472 * kg5)) * popm3034
			LLER += nutm3034
			totalPop += popm3034
			sexAge = "3034_M"
			groupList.append(sexAge)
			
		#The female 35-39 age group
		elif "3539_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf3539 = array.sum()
			nutf3539 = (1.55 * (845.6 + 8.118 * kg5)) * popf3539
			LLER += nutf3539
			totalPop += popf3539
			sexAge = "3539_F"
			groupList.append(sexAge)
		
		#The male 35-39 age group
		elif "3539_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm3539 = array.sum()
			nutm3539 = (1.55 * (873.1 + 11.472 * kg5)) * popm3539
			LLER += nutm3539
			totalPop += popm3539
			sexAge = "3539_M"
			groupList.append(sexAge)
			
		#The female 40-44 age group
		elif "4044_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf4044 = array.sum()
			nutf4044 = (1.55 * (845.6 + 8.118 * kg5)) * popf4044
			LLER += nutf4044
			totalPop += popf4044
			sexAge = "4044_F"
			groupList.append(sexAge)
			
		#The male 40-44 age group
		elif "4044_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm4044 = array.sum()
			nutm4044 = (1.55 * (873.1 + 11.472 * kg5)) * popm4044
			LLER += nutm4044
			totalPop += popm4044
			sexAge = "4044_M"
			groupList.append(sexAge)
			
		#The female 45-49 age group
		elif "4549_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf4549 = array.sum()
			nutf4549 = (1.55 * (845.6 + 8.118 * kg5)) * popf4549
			LLER += nutf4549
			totalPop += popf4549
			sexAge = "4549_F"
			groupList.append(sexAge)
			
		#The male 45-49 age group
		elif "4549_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm4549 = array.sum()
			nutm4549 = (1.55 * (873.1 + 11.472 * kg5)) * popm4549
			LLER += nutm4549
			totalPop += popm4549
			sexAge = "4549_M"
			groupList.append(sexAge)
			
		#The female 50-54 age group
		elif "5054_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf5054 = array.sum()
			nutf5054 = (1.55 * (845.6 + 8.118 * kg5)) * popf5054
			LLER += nutf5054
			totalPop += popf5054
			sexAge = "5054_F"
			groupList.append(sexAge)
			
		#The male 50-54 age group
		elif "5054_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm5054 = array.sum()
			nutm5054 = (1.55 * (873.1 + 11.472 * kg5)) * popm5054
			LLER += nutm5054
			totalPop += popm5054
			sexAge = "5054_M"
			groupList.append(sexAge)
			
		#The female 55-59 age group
		elif "5559_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf5559 = array.sum()
			nutf5559 = (1.55 * (845.6 + 8.118 * kg5)) * popf5559
			LLER += nutf5559
			totalPop += popf5559
			sexAge = "5559_F"
			groupList.append(sexAge)
			
		#The male 55-59 age group
		elif "5559_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm5559 = array.sum()
			nutm5559 = (1.55 * (873.1 + 11.472 * kg5)) * popm5559
			LLER += nutm5559
			totalPop += popm5559
			sexAge = "5559_M"
			groupList.append(sexAge)
			
		#The female 60-64 age group
		elif "6064_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf6064 = array.sum()
			nutf6064 = (1.55 * (658.5 + 9.082 * kg5)) * popf6064
			LLER += nutf6064
			totalPop += popf6064
			sexAge = "6064_F"
			groupList.append(sexAge)
			
		#The male 60-64 age group
		elif "6064_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm6064 = array.sum()
			nutm6064 = (1.55 * (587.7 + 11.711 * kg5)) * popm6064
			LLER += nutm6064
			totalPop += popm6064
			sexAge = "6064_M"
			groupList.append(sexAge)
			
		#The female 65+ age group
		elif "65PL_F" in r:
			height = (femaleStatureInt / 161.8) * 163.3383
			kg5 = 17.38 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf65pl = array.sum()
			nutf65pl = (1.55 * (658.5 + 9.082 * kg5)) * popf65pl
			LLER += nutf65pl
			totalPop += popf65pl
			sexAge = "65PL_F"
			groupList.append(sexAge)
			
		#The male 65+ age group
		elif "65PL_M" in r:
			height = (maleStatureInt / 175.7) * 176.8492
			kg5 = 18.66 * ((height / 100)**2)
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm65pl = array.sum()
			nutm65pl = (1.55 * (587.7 + 11.711 * kg5)) * popm65pl
			LLER += nutm65pl
			totalPop += popm65pl
			sexAge = "65PL_M"
			groupList.append(sexAge)
			
		else:
			arcpy.AddMessage("Calculating Nutrition Metrics for AOI... ")
			
	#The Africa continent rasterList does not include a WorldPop layer for m65pl 2020. Make this a missing value.
	if "65PL_M" not in groupList and year == "2020":
		popm65pl = 999999999
		nutm65pl = 999999999
	
	#Append the Nutrition Information to a copy of the AOI
	#Create copy
	copyAOI = arcpy.CopyFeatures_management(AOI, os.path.join(arcpy.env.scratchFolder, "intOutput", "copyAOI"))
	
	#Remove all fields and rows from the copy
	fieldObjList = arcpy.ListFields(copyAOI)
	fieldNameList = []
	for field in fieldObjList:
		if not field.required:
			fieldNameList.append(field.name)
	fieldNameList2 = fieldNameList[1:]    #Need to leave at least one of the fields
	if len(fieldNameList2) >= 1:
		arcpy.DeleteField_management(copyAOI, fieldNameList2)
	dissolveField = ""
	for field in fieldObjList:
		if field.type == "OID":
			dissolveField = field.name
			break
		else:
			arcpy.AddField_management(copyAOI, "uniqueID", "LONG")
			with arcpy.da.UpdateCursor(copyAOI, "uniqueID") as cursor:
				for row in cursor:
					row[0] = autoIncrement()
					cursor.updateRow(row)
				del cursor
			fields = arcpy.ListFields(copyAOI)
			for field in fields:
				if field.name == "uniqueID":
					dissolveField = field.name
	copyAOIDis = arcpy.Dissolve_management(copyAOI, os.path.join(arcpy.env.scratchFolder, "intOutput", "copyAOIDis"), dissolveField)
	arcpy.AddField_management(copyAOIDis, "ageGroup", "TEXT")
	arcpy.AddField_management(copyAOIDis, "Pop", "DOUBLE", "", 5)
	arcpy.AddField_management(copyAOIDis, "LLER", "DOUBLE", "", 5)
	
	#The list of values that are added to the final shapefile
	list = [("m0004", popm0004, nutm0004), ("f0509", popf0509, nutf0509), ("m0509", popm0509, nutm0509), ("f1014", popf1014, nutf1014),
			("m1014", popm1014, nutm1014), ("f1519", popf1519, nutf1519), ("m1519", popm1519, nutm1519), ("f2024", popf2024, nutf2024), ("m2024", popm2024, nutm2024),
			("f2529", popf2529, nutf2529), ("m2529", popm2529, nutm2529), ("f3034", popf3034, nutf3034), ("m3034", popm3034, nutm3034), ("f3539", popf3539, nutf3539),
			("m3539", popm3539, nutm3539), ("f4044", popf4044, nutf4044), ("m4044", popm4044, nutm4044), ("f4549", popf4549, nutf4549), ("m4549", popm4549, nutm4549),
			("f5054", popf5054, nutf5054), ("m5054", popm5054, nutm5054), ("f5559", popf5559, nutf5559), ("m5559", popm5559, nutm5559), ("f6064", popf6064, nutf6064),
			("m6064", popm6064, nutm6064), ("f65pl", popf65pl, nutf65pl), ("m65pl", popm65pl, nutm65pl), ("total", totalPop, LLER)]
	
	#Add values to Shapefile Attribute Table
	c = arcpy.da.InsertCursor(copyAOIDis, ("ageGroup", "Pop", "LLER"))
	for row in list:
		c.insertRow(row)
	del c
	
	#Update the first row
	field = "ageGroup"
	ageGroup = "f0004"
	Pop = popf0004
	LLER = nutf0004
	queryString = '"' + field + '" = ' + "'" "'"
	with arcpy.da.UpdateCursor(copyAOIDis, ("ageGroup", "Pop", "LLER"), queryString) as cursor:
		for row in cursor:
			row[0] = ageGroup
			row[1] = Pop
			row[2] = LLER
			cursor.updateRow(row)
	
	#Output the final shapefile
	result = arcpy.CopyFeatures_management(copyAOIDis, os.path.join(arcpy.env.scratchFolder, "intOutput", "finalOutput"))
	
	#Create a csv file with information from the attribute table
	table = arcpy.TableToTable_conversion(result, arcpy.env.scratchFolder, "outputTable.dbf")

	
if __name__ == '__main__':
	isLicensed()
	
	#Get the values of the input parameters
	AOI = arcpy.GetParameterAsText(0)
	rasterFolder = arcpy.GetParameterAsText(1)
	year = arcpy.GetParameterAsText(2)
	maleStature = arcpy.GetParameterAsText(3)
	femaleStature = arcpy.GetParameterAsText(4)
	
	###-----------------------------------------------------------------------------------###
	#The below content has been commented out, but will be used in the geo web app
	
	#This is the path to the mosaic database with demographic information
	#if continent == "Africa":
	#	mosaicDB = "Z:\\Francesco Tonini\\Telecoupling\\Data\\TelecouplingDB.gdb\\WorldPop_AgeStructures_1km_Africa"
	#elif continent == "Asia":
	#	mosaicDB = "Z:\\Francesco Tonini\\Telecoupling\\Data\\TelecouplingDB.gdb\\WorldPop_AgeStructures_1km_Asia"
	#else:
	#	mosaicDB = "Z:\\Francesco Tonini\\Telecoupling\\Data\\TelecouplingDB.gdb\\WorldPop_AgeStructures_1km_LAC"
	#arcpy.AddMessage("continent is " + continent)
	#Run the Nutrition Metrics tool
	
	#End commented out section
	###-----------------------------------------------------------------------------------###
	
	#global to increment over records
	rec = 0
	
	#obtain a list of rasters for the chosen continent
	arcpy.env.workspace = rasterFolder
	rasterList = arcpy.ListRasters()
	
	
	#Run the nutrition function
	try:
		nutritionMetrics(AOI, year, maleStature, femaleStature, rasterList)
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
	result = os.path.join(arcpy.env.scratchFolder, "intOutput", "finalOutput.shp")
	copyresult = arcpy.CopyFeatures_management(result, os.path.join(arcpy.env.scratchFolder, "finalOutput"))
	table = os.path.join(arcpy.env.scratchFolder, "outputTable.dbf")
	#Remove the scratch folder and add output to map.
	os.chdir(arcpy.env.scratchFolder)
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intOutput'))
	arcpy.SetParameter(5, copyresult)
	arcpy.SetParameter(6, table)
	#I'll need to add some code here to also output a csv (dbf) file