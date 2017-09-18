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

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True

def nutritionMetrics(AOI, year, maleStature, femaleStature, outRaster, mosaicDB):

	#Create intermediate folder where output will be temporarily saved
	arcpy.CreateFolder_management(arcpy.env.scratchFolder, "intOutput")
	arcpy.AddMessage("foldercreated")
	os.chdir(os.path.join(arcpy.env.scratchFolder, "intOutput"))
	arcpy.AddMessage("made it here")
	
	#Export only images consistent with the Year and Area of Interest
	query = "Year = " + year
	basename = "ageStructure_" 
	arcpy.ExportMosaicDatasetItems_management(mosaicDB, os.path.join(arcpy.env.scratchFolder, "intOutput"), basename, query, "", "", "FEATURE_CLASS", AOI)
	
	#Clip the exported extents by the AOI
	for file in os.listdir(os.path.join(arcpy.env.scratchFolder, "intOutput")):
		if file.endswith(".TIF"):
			rasterName = file.split(".")[0]
			rasterName = rasterName + ".img"
			outExtractByMask = ExtractByMask(file, AOI)
			outExtractByMask.save(os.path.join(arcpy.env.scratchFolder, "intOutput", rasterName))
			os.remove(file)
	
	#Loop through the exported rasters and calculate nutrition metrics for each rasters
	rasterList = []
	for file in os.listdir(os.path.join(arcpy.env.scratchFolder, "intOutput")):
		if file.endswith(".img"):
			rasterList.append(file)
	arcpy.AddMessage(rasterList)
	
	#Calculate nutrition metrics
	LLER = 0    #This will keep the tally of 'Lower Limit of Energy Requirement' in kcal/day for the study area (AOI).
	totalPop = 0    #This will keep the tally of total population in the study area (AOI).
	regex = re.compile(r'\d+')    #Recognizes numerical values in raster names.  This will be used to capture OID values.
	maleStatureInt = int(maleStature)
	femaleStatureInt = int(femaleStature)
	for r in rasterList:
		OID = regex.findall(r)[0]
		
		#The appropriate equation is added to each age group and a running tally of LLER is kept.
		#The female 00-04 age group
		if OID in ["1", "2", "3", "4", "5"]:
			arcpy.AddMessage("Calculating calorie requirement for female 00 - 04 age group.")
			height = (femaleStatureInt / 161.8) * 84.97556    #note that 2014 heights for Americans are used to standardized height values (CDC, 2016)
			arcpy.AddMessage("female height for f0004 is " + str(height))
			kg50 = 15.5 * ((height / 100)**2)
			arcpy.AddMessage("kg50 for f0004 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf0004 = array.sum()
			arcpy.AddMessage("population for f0004 is " + str(popf0004))
			nutf0004 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (6.3 * 2)) * popf0004
			arcpy.AddMessage("LLER for f0004 age group(total kcal/day): " + str(nutf0004))
			LLER += nutf0004
			totalPop += popf0004
			arcpy.AddMessage("Total LLER is " + str(LLER))
		
		#The male 00-04 age group
		elif OID in ["6", "7", "8", "9", "10"]:
			arcpy.AddMessage("Calculating calorie requirement for male 00 - 04 age group.")
			height = (maleStatureInt / 175.7) * 86.4522
			arcpy.AddMessage("male height for m0004 is " + str(height))
			kg50 = 15.8 * ((height / 100)**2)
			arcpy.AddMessage("kg50 for m0004 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm0004 = array.sum()
			arcpy.AddMessage("population for m0004 is " + str(popm0004))
			nutm0004 = ((310.2 + 63.3 * kg50 - 0.263 * (kg50)**2) + (6.3 * 2)) * popm0004
			arcpy.AddMessage("LLER for m0004 age group (total kcal/day): " + str(nutm0004))
			LLER += nutm0004
			totalPop += popm0004
			arcpy.AddMessage("Total LLER for m and f 0004 is: " + str(LLER))
		
		#The female 05-09 age group
		elif OID in ["11", "12", "13", "14", "15"]:
			arcpy.AddMessage("Calculating calorie requirement for female 05 - 09 age group.")
			height = (femaleStatureInt / 161.8) * 121.7617
			#arcpy.AddMessage("female height for f0509 is " + str(height))
			kg50 = 15.52 * ((height / 100)**2)
			#arcpy.AddMessage("kg50 for f0509 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf0509 = array.sum()
			#arcpy.AddMessage("population for f0509 is " + str(popf0509))
			nutf0509 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (8.22 * 2)) * popf0509
			arcpy.AddMessage("LLER for f0509 age group (total kcal/day): " + str(nutf0509))
			LLER += nutf0509
			totalPop += popf0509
			#arcpy.AddMessage("Total LLER up to f 0509 is: " + str(LLER))
			
		#The male 05-09 age group
		elif OID in ["16", "17", "18", "19", "20"]:
			arcpy.AddMessage("Calculating calorie requirement for male 05 - 09 age group.")
			height = (maleStatureInt / 175.7) * 122.0305
			#arcpy.AddMessage("male height for m0509 is " + str(height))
			kg50 = 15.6 * ((height / 100)**2)
			#arcpy.AddMessage("kg50 for m0509 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm0509 = array.sum()
			#arcpy.AddMessage("population for m0509 is " + str(popm0509))
			nutm0509 = ((310.2 + 63.3 * kg50 - 0.263 * (kg50)**2) + (6.58 * 2)) * popm0509
			arcpy.AddMessage("LLER for m0509 age group (total kcal/day): " + str(nutm0509))
			LLER += nutm0509
			totalPop += popm0509
			#arcpy.AddMessage ("Total LLER is: " + str(LLER))
			
		#The female 10-14 age group
		elif OID in ["21", "22", "23", "24", "25"]:
			arcpy.AddMessage("Calculating calorie requirement for female 10 - 14 age group.")
			height = (femaleStatureInt / 161.8) * 151.4866
			#arcpy.AddMessage("female height for f1014 is " + str(height))
			kg5 = 15.19 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for f1014 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf1014 = array.sum()
			#arcpy.AddMessage("population for f1014 is " + str(popf1014))
			nutf1014 = (0.85 * (263.4 + 65.3 * kg5 - 0.454 * (kg5)**2) + (9.86 * 2)) * popf1014
			arcpy.AddMessage("LLER for f1014 age group (total kcal/day): " + str(nutf1014))
			LLER += nutf1014
			totalPop += popf1014
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 10-14 age group
		elif OID in ["26", "27", "28", "29", "30"]:
			arcpy.AddMessage("Calculating calorie requirement for male 10 - 14 age group.")
			height = (maleStatureInt / 175.7) * 149.3088
			#arcpy.AddMessage("male height for m1014 is " + str(height))
			kg5 = 15.14 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for m1014 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm1014 = array.sum()
			#arcpy.AddMessage("population for m1014 is " + str(popm1014))
			nutm1014 = (0.85 * (310.2 + 63.3 * kg5 - 0.263 * (kg5)**2) + (10.41 * 2)) * popm1014
			arcpy.AddMessage("LLER for m1014 age group (total kcal/day): " + str(nutm1014))
			LLER += nutm1014
			totalPop += popm1014
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 15-19 age group
		elif OID in ["31", "32", "33", "34", "35"]:
			arcpy.AddMessage("Calculating calorie requirement for female 15 - 19 age group.")
			height = (femaleStatureInt / 161.8) * 163.1308
			#arcpy.AddMessage("female height for f1519 is " + str(height))
			kg5 = 17.19 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for f1519 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf1519 = array.sum()
			#arcpy.AddMessage("population for f1519 is " + str(popf1519))
			nutf1519 = (1.55 * (486.6 + 8.126 * kg5)) * popf1519
			arcpy.AddMessage("LLER for f1519 age group (total kcal/day): " + str(nutf1519))
			LLER += nutf1519
			totalPop += popf1519
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 15-19 age group
		elif OID in ["36", "37", "38", "39", "40"]:
			arcpy.AddMessage("Calculating calorie requirement for male 15 - 19 age group.")
			height = (maleStatureInt / 175.7) * 176.185
			#arcpy.AddMessage("male height for m1519 is " + str(height))
			kg5 = 18.10 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for m1519 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm1519 = array.sum()
			#arcpy.AddMessage("population for m1519 is " + str(popm1519))
			nutm1519 = (1.55 * (692.2 + 15.057 * kg5)) * popm1519
			arcpy.AddMessage("LLER for m1519 age group (total kcal/day): " + str(nutm1519))
			LLER += nutm1519
			totalPop += popm1519
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 20-24 age group
		elif OID in ["41", "42", "43", "44", "45"]:
			arcpy.AddMessage("Calculating calorie requirement for female 20 - 24 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			#arcpy.AddMessage("female height for f2024 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for f2024 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf2024 = array.sum()
			#arcpy.AddMessage("population for f2024 is " + str(popf2024))
			nutf2024 = (1.55 * (486.6 + 8.126 * kg5)) * popf2024
			arcpy.AddMessage("LLER for f2024 age group (total kcal/day): " + str(nutf2024))
			LLER += nutf2024
			totalPop += popf2024
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 20-24 age group
		elif OID in ["46", "47", "48", "49", "50"]:
			arcpy.AddMessage("Calculating calorie requirement for male 20 - 24 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m2024 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m2024 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm2024 = array.sum()
			arcpy.AddMessage("population for m2024 is " + str(popm2024))
			nutm2024 = (1.55 * (692.2 + 15.057 * kg5)) * popm2024
			arcpy.AddMessage("LLER for m2024 age group (total kcal/day): " + str(nutm2024))
			LLER += nutm2024
			totalPop += popm2024
			arcpy.AddMessage("Total LLER is: " + str(LLER))
		
		#The female 25-29 age group
		elif OID in ["51", "52", "53", "54", "55"]:
			arcpy.AddMessage("Calculating calorie requirement for female 25 - 29 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f2529 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f2529 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf2529 = array.sum()
			arcpy.AddMessage("population for f2529 is " + str(popf2529))
			nutf2529 = (1.55 * (486.6 + 8.126 * kg5)) * popf2529
			arcpy.AddMessage("LLER for f2529 age group (total kcal/day): " + str(nutf2529))
			LLER += nutf2529
			totalPop += popf2529
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 25-29 age group 
		elif OID in ["56", "57", "58", "59", "60"]:
			arcpy.AddMessage("Calculating calorie requirement for male 25 - 29 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m2529 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m2529 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm2529 = array.sum()
			arcpy.AddMessage("population for m2529 is " + str(popm2529))
			nutm2529 = (1.55 * (692.2 + 15.057 * kg5)) * popm2529
			arcpy.AddMessage("LLER for m2529 age group (total kcal/day): " + str(nutm2529))
			LLER += nutm2529
			totalPop += popm2529
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 30-34 age group
		elif OID in ["61", "62", "63", "64", "65"]:
			arcpy.AddMessage("Calculating calorie requirement for female 30 - 34 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f3034 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f3034 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf3034 = array.sum()
			arcpy.AddMessage("population for f3034 is " + str(popf3034))
			nutf3034 = (1.55 * (845.6 + 8.118 * kg5)) * popf3034
			arcpy.AddMessage("LLER for f3034 age group (total kcal/day): " + str(nutf3034))
			LLER += nutf3034
			totalPop += popf3034
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 30-34 age group
		elif OID in ["66", "67", "68", "69", "70"]:
			arcpy.AddMessage("Calculating calorie requirement for male 30 - 34 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m3034 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m3034 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm3034 = array.sum()
			arcpy.AddMessage("population for m3034 is " + str(popm3034))
			nutm3034 = (1.55 * (873.1 + 11.472 * kg5)) * popm3034
			arcpy.AddMessage("LLER for m3034 age group (total kcal/day): " + str(nutm3034))
			LLER += nutm3034
			totalPop += popm3034
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 35-39 age group
		elif OID in ["71", "72", "73", "74", "75"]:
			arcpy.AddMessage("Calculating calorie requirement for female 35 - 39 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f3539 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f3539 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf3539 = array.sum()
			arcpy.AddMessage("population for f3539 is " + str(popf3539))
			nutf3539 = (1.55 * (845.6 + 8.118 * kg5)) * popf3539
			arcpy.AddMessage("LLER for f3539 age group (total kcal/day): " + str(nutf3539))
			LLER += nutf3539
			totalPop += popf3539
			arcpy.AddMessage("Total LLER is: " + str(LLER))
		
		#The male 35-39 age group
		elif OID in ["76", "77", "78", "79", "80"]:
			arcpy.AddMessage("Calculating calorie requirement for male 35 - 39 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m3539 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m3539 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm3539 = array.sum()
			arcpy.AddMessage("population for m3539 is " + str(popm3539))
			nutm3539 = (1.55 * (873.1 + 11.472 * kg5)) * popm3539
			arcpy.AddMessage("LLER for m3539 age group (total kcal/day): " + str(nutm3539))
			LLER += nutm3539
			totalPop += popm3539
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 40-44 age group
		elif OID in ["81", "82", "83", "84", "85"]:
			arcpy.AddMessage("Calculating calorie requirement for female 40 - 44 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f4044 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f4044 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf4044 = array.sum()
			arcpy.AddMessage("population for f4044 is " + str(popf4044))
			nutf4044 = (1.55 * (845.6 + 8.118 * kg5)) * popf4044
			arcpy.AddMessage("LLER for f4044 age group (total kcal/day): " + str(nutf4044))
			LLER += nutf4044
			totalPop += popf4044
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 40-44 age group
		elif OID in ["86", "87", "88", "89", "90"]:
			arcpy.AddMessage("Calculating calorie requirement for male 40 - 44 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m4044 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m4044 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm4044 = array.sum()
			arcpy.AddMessage("population for m4044 is " + str(popm4044))
			nutm4044 = (1.55 * (873.1 + 11.472 * kg5)) * popm4044
			arcpy.AddMessage("LLER for m4044 age group (total kcal/day): " + str(nutm4044))
			LLER += nutm4044
			totalPop += popm4044
			arcpy.AddMessage("Total LLER is " + str(LLER))
			
		#The female 45-49 age group
		elif OID in ["91", "92", "93", "94", "95"]:
			arcpy.AddMessage("Calculating calorie requirement for female 45 - 49.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f4549 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f4549 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf4549 = array.sum()
			arcpy.AddMessage("population for f4549 is " + str(popf4549))
			nutf4549 = (1.55 * (845.6 + 8.118 * kg5)) * popf4549
			arcpy.AddMessage("LLER for f4549 age group (total kcal/day): " + str(nutf4549))
			LLER += nutf4549
			totalPop += popf4549
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 45-49 age group
		elif OID in ["96", "97", "98", "99", "100"]:
			arcpy.AddMessage("Calculating calorie requirement for male 45 - 49.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m4549 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m4549 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm4549 = array.sum()
			arcpy.AddMessage("population for m4549 is " + str(popm4549))
			nutm4549 = (1.55 * (873.1 + 11.472 * kg5)) * popm4549
			arcpy.AddMessage("LLER for m4549 age group (total kcal/day): " + str(nutm4549))
			LLER += nutm4549
			totalPop += popm4549
			arcpy.AddMessage("Total LLER is " + str(LLER))
			
		#The female 50-54 age group
		elif OID in ["101", "102", "103", "104", "105"]:
			arcpy.AddMessage("Calculating calorie requirement for female 50 - 54.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f5054 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f5054 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf5054 = array.sum()
			arcpy.AddMessage("population for f5054 is " + str(popf5054))
			nutf5054 = (1.55 * (845.6 + 8.118 * kg5)) * popf5054
			arcpy.AddMessage("LLER for f5054 age group (total kcal/day): " + str(nutf5054))
			LLER += nutf5054
			totalPop += popf5054
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 50-54 age group
		elif OID in ["106", "107", "108", "109", "110"]:
			arcpy.AddMessage("Calculating calorie requirement for male 50 - 54.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m5054 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m5054 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm5054 = array.sum()
			arcpy.AddMessage("population for m5054 is " + str(popm5054))
			nutm5054 = (1.55 * (873.1 + 11.472 * kg5)) * popm5054
			arcpy.AddMessage("LLER for m5054 age group (total kcal/day): " + str(nutm5054))
			LLER += nutm5054
			totalPop += popm5054
			arcpy.AddMessage("Total LLER is " + str(LLER))
			
		#The female 55-59 age group
		elif OID in ["111", "112", "113", "114", "115"]:
			arcpy.AddMessage("Calculating calorie requirement for female 55 - 59.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f5559 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f5559 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf5559 = array.sum()
			arcpy.AddMessage("population for f5559 is " + str(popf5559))
			nutf5559 = (1.55 * (845.6 + 8.118 * kg5)) * popf5559
			arcpy.AddMessage("LLER for f5559 age group (total kcal/day): " + str(nutf5559))
			LLER += nutf5559
			totalPop += popf5559
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 55-59 age group
		elif OID in ["116", "117", "118", "119", "120"]:
			arcpy.AddMessage("Calculating calorie requirement for male 55 - 59.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m5559 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m5559 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm5559 = array.sum()
			arcpy.AddMessage("population for m5559 is " + str(popm5559))
			nutm5559 = (1.55 * (873.1 + 11.472 * kg5)) * popm5559
			arcpy.AddMessage("LLER for m5559 age group (total kcal/day): " + str(nutm5559))
			LLER += nutm5559
			totalPop += popm5559
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 60-64 age group
		elif OID in ["121", "122", "123", "124", "125"]:
			arcpy.AddMessage("Calculating calorie requirement for female 60 - 64.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f6064 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f6064 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf6064 = array.sum()
			arcpy.AddMessage("population for f6064 is " + str(popf6064))
			nutf6064 = (1.55 * (658.5 + 9.082 * kg5)) * popf6064
			arcpy.AddMessage("LLER for f6064 age group (total kcal/day): " + str(nutf6064))
			LLER += nutf6064
			totalPop += popf6064
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 60-64 age group
		elif OID in ["126", "127", "128", "129", "130"]:
			arcpy.AddMessage("Calculating calorie requirement for male 60 - 64.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m6064 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m6064 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm6064 = array.sum()
			arcpy.AddMessage("population for m6064 is " + str(popm6064))
			nutm6064 = (1.55 * (587.7 + 11.711 * kg5)) * popm6064
			arcpy.AddMessage("LLER for m6064 age group (total kcal/day): " + str(nutm6064))
			LLER += nutm6064
			totalPop += popm6064
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 65+ age group
		elif OID in ["131", "132", "133", "134", "135"]:
			arcpy.AddMessage("Calculating calorie requirement for female 65+.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f65+ is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f65+ is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popf65pl = array.sum()
			arcpy.AddMessage("population for f65+ is " + str(popf65pl))
			nutf65pl = (1.55 * (658.5 + 9.082 * kg5)) * popf65pl
			arcpy.AddMessage("LLER for f65pl age group (total kcal/day): " + str(nutf65pl))
			LLER += nutf65pl
			totalPop += popf65pl
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 65+ age group
		elif OID in ["136", "137", "138", "139", "140"]:
			arcpy.AddMessage("Calculating calorie requirement fo male 65+.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m65+ is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m65+ is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r, "", "", "", 0)
			popm65pl = array.sum()
			arcpy.AddMessage("population for m65+ is " + str(popm65pl))
			nutm65pl = (1.55 * (587.7 + 11.711 * kg5)) * popm65pl
			arcpy.AddMessage("LLER for m65pl age group (total kcal/day): " + str(nutm65pl))
			LLER += nutm65pl
			totalPop += popm65pl
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			arcpy.AddMessage("Total population is " + str(totalPop))
			
		else:
			arcpy.AddMessage("Age group and/or Year for " + str(OID) + " does not exist")
			
	#Append the Nutrition Information to a copy of the AOI
	
	#Create copy
	copyAOI = arcpy.CopyFeatures_management(AOI, os.path.join(arcpy.env.scratchFolder, "intOutput", "copyAOI"))
	
	#Remove all fields and rows from the copy
	fieldObjList = arcpy.ListFields(copyAOI)
	fieldNameList = []
	for field in fieldObjList:
		if not field.required:
			fieldNameList.append(field.name)
	fieldNameList = fieldNameList[1:]    #Need to leave at least one of the fields
	arcpy.DeleteField_management(copyAOI, fieldNameList)
	dissolveField = ""
	for field in fieldObjList:
		if field.type == "OID":
			dissolveField = field.name
	
	
	
	
if __name__ == '__main__':
	#Get the values of the input parameters
	AOI = arcpy.GetParameterAsText(0)
	mosaicDB = arcpy.GetParameterAsText(1)
	year = arcpy.GetParameterAsText(2)
	maleStature = arcpy.GetParameterAsText(3)
	femaleStature = arcpy.GetParameterAsText(4)
	outRaster = arcpy.GetParameterAsText(5)
	
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
	
	
	try:
		nutritionMetrics(AOI, year, maleStature, femaleStature, outRaster, mosaicDB)
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))