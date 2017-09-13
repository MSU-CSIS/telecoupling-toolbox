# Created on 2017-8-31
# Usage: Lower Limit of Energy Requirements (LLER) for area of interest.
#--------------------------------------------------------------------------------------------------------------

#Import all necessary module dependencies
import arcpy
import numpy
import os
import re

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
	
	#Loop through the exported rasters and calculate nutrition metrics for each rasters
	rasterList = []
	for file in os.listdir(os.path.join(arcpy.env.scratchFolder, "intOutput")):
		if file.endswith(".TIF"):
			rasterList.append(file)
	arcpy.AddMessage(rasterList)
	
	#Calculate nutrition metrics
	LLER = 0    #This will keep the tally of 'Lower Limit of Energy Requirement' in kcal/day for the study area.
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
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f0004 is " + str(pop))
			f0004 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (6.3 * 2)) * pop
			arcpy.AddMessage("LLER for f0004 age group(total kcal/day): " + str(f0004))
			LLER += f0004
			arcpy.AddMessage("Total LLER is " + str(LLER))
		
		#The male 00-04 age group
		elif OID in ["6", "7", "8", "9", "10"]:
			arcpy.AddMessage("Calculating calorie requirement for male 00 - 04 age group.")
			height = (maleStatureInt / 175.7) * 86.4522
			arcpy.AddMessage("male height for m0004 is " + str(height))
			kg50 = 15.8 * ((height / 100)**2)
			arcpy.AddMessage("kg50 for m0004 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m0004 is " + str(pop))
			m0004 = ((310.2 + 63.3 * kg50 - 0.263 * (kg50)**2) + (6.3 * 2)) * pop
			arcpy.AddMessage("LLER for m0004 age group (total kcal/day): " + str(m0004))
			LLER += m0004
			arcpy.AddMessage("Total LLER for m and f 0004 is: " + str(LLER))
		
		#The female 05-09 age group
		elif OID in ["11", "12", "13", "14", "15"]:
			arcpy.AddMessage("Calculating calorie requirement for female 05 - 09 age group.")
			height = (femaleStatureInt / 161.8) * 121.7617
			#arcpy.AddMessage("female height for f0509 is " + str(height))
			kg50 = 15.52 * ((height / 100)**2)
			#arcpy.AddMessage("kg50 for f0509 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for f0509 is " + str(pop))
			f0509 = ((263.4 + 65.3 * kg50 - 0.454 * (kg50)**2) + (8.22 * 2)) * pop
			arcpy.AddMessage("LLER for f0509 age group (total kcal/day): " + str(f0509))
			LLER += f0509
			#arcpy.AddMessage("Total LLER up to f 0509 is: " + str(LLER))
			
		#The male 05-09 age group
		elif OID in ["16", "17", "18", "19", "20"]:
			arcpy.AddMessage("Calculating calorie requirement for male 05 - 09 age group.")
			height = (maleStatureInt / 175.7) * 122.0305
			#arcpy.AddMessage("male height for m0509 is " + str(height))
			kg50 = 15.6 * ((height / 100)**2)
			#arcpy.AddMessage("kg50 for m0509 is " + str(kg50))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for m0509 is " + str(pop))
			m0509 = ((310.2 + 63.3 * kg50 - 0.263 * (kg50)**2) + (6.58 * 2)) * pop
			arcpy.AddMessage("LLER for m0509 age group (total kcal/day): " + str(m0509))
			LLER += m0509
			#arcpy.AddMessage ("Total LLER is: " + str(LLER))
			
		#The female 10-14 age group
		elif OID in ["21", "22", "23", "24", "25"]:
			arcpy.AddMessage("Calculating calorie requirement for female 10 - 14 age group.")
			height = (femaleStatureInt / 161.8) * 151.4866
			#arcpy.AddMessage("female height for f1014 is " + str(height))
			kg5 = 15.19 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for f1014 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for f1014 is " + str(pop))
			f1014 = (0.85 * (263.4 + 65.3 * kg5 - 0.454 * (kg5)**2) + (9.86 * 2)) * pop
			arcpy.AddMessage("LLER for f1014 age group (total kcal/day): " + str(f1014))
			LLER += f1014
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 10-14 age group
		elif OID in ["26", "27", "28", "29", "30"]:
			arcpy.AddMessage("Calculating calorie requirement for male 10 - 14 age group.")
			height = (maleStatureInt / 175.7) * 149.3088
			#arcpy.AddMessage("male height for m1014 is " + str(height))
			kg5 = 15.14 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for m1014 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for m1014 is " + str(pop))
			m1014 = (0.85 * (310.2 + 63.3 * kg5 - 0.263 * (kg5)**2) + (10.41 * 2)) * pop
			arcpy.AddMessage("LLER for m1014 age group (total kcal/day): " + str(m1014))
			LLER += m1014
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 15-19 age group
		elif OID in ["31", "32", "33", "34", "35"]:
			arcpy.AddMessage("Calculating calorie requirement for female 15 - 19 age group.")
			height = (femaleStatureInt / 161.8) * 163.1308
			#arcpy.AddMessage("female height for f1519 is " + str(height))
			kg5 = 17.19 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for f1519 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for f1519 is " + str(pop))
			f1519 = (1.55 * (486.6 + 8.126 * kg5)) * pop
			arcpy.AddMessage("LLER for f1519 age group (total kcal/day): " + str(f1519))
			LLER += f1519
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 15-19 age group
		elif OID in ["36", "37", "38", "39", "40"]:
			arcpy.AddMessage("Calculating calorie requirement for male 15 - 19 age group.")
			height = (maleStatureInt / 175.7) * 176.185
			#arcpy.AddMessage("male height for m1519 is " + str(height))
			kg5 = 18.10 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for m1519 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for m1519 is " + str(pop))
			m1519 = (1.55 * (692.2 + 15.057 * kg5)) * pop
			arcpy.AddMessage("LLER for m1519 age group (total kcal/day): " + str(m1519))
			LLER += m1519
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 20-24 age group
		elif OID in ["41", "42", "43", "44", "45"]:
			arcpy.AddMessage("Calculating calorie requirement for female 20 - 24 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			#arcpy.AddMessage("female height for f2024 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			#arcpy.AddMessage("kg5 for f2024 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			#arcpy.AddMessage("population for f2024 is " + str(pop))
			f2024 = (1.55 * (486.6 + 8.126 * kg5)) * pop
			arcpy.AddMessage("LLER for f2024 age group (total kcal/day): " + str(f2024))
			LLER += f2024
			#arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 20-24 age group
		elif OID in ["46", "47", "48", "49", "50"]:
			arcpy.AddMessage("Calculating calorie requirement for male 20 - 24 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m2024 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m2024 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m2024 is " + str(pop))
			m2024 = (1.55 * (692.2 + 15.057 * kg5)) * pop
			arcpy.AddMessage("LLER for m2024 age group (total kcal/day): " + str(m2024))
			LLER += m2024
			arcpy.AddMessage("Total LLER is: " + str(LLER))
		
		#The female 25-29 age group
		elif OID in ["51", "52", "53", "54", "55"]:
			arcpy.AddMessage("Calculating calorie requirement for female 25 - 29 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f2529 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f2529 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f2529 is " + str(pop))
			f2529 = (1.55 * (486.6 + 8.126 * kg5)) * pop
			arcpy.AddMessage("LLER for f2529 age group (total kcal/day): " + str(f2529))
			LLER += f2529
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 25-29 age group 
		elif OID in ["56", "57", "58", "59", "60"]:
			arcpy.AddMessage("Calculating calorie requirement for male 25 - 29 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m2529 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m2529 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m2529 is " + str(pop))
			m2529 = (1.55 * (692.2 + 15.057 * kg5)) * pop
			arcpy.AddMessage("LLER for m2529 age group (total kcal/day): " + str(m2529))
			LLER += m2529
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 30-34 age group
		elif OID in ["61", "62", "63", "64", "65"]:
			arcpy.AddMessage("Calculating calorie requirement for female 30 - 34 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f3034 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f3034 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f3034 is " + str(pop))
			f3034 = (1.55 * (845.6 + 8.118 * kg5)) * pop
			arcpy.AddMessage("LLER for f3034 age group (total kcal/day): " + str(f3034))
			LLER += f3034
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 30-34 age group
		elif OID in ["66", "67", "68", "69", "70"]:
			arcpy.AddMessage("Calculating calorie requirement for male 30 - 34 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m3034 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m3034 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m3034 is " + str(pop))
			m3034 = (1.55 * (873.1 + 11.472 * kg5)) * pop
			arcpy.AddMessage("LLER for m3034 age group (total kcal/day): " + str(m3034))
			LLER += m3034
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 35-39 age group
		elif OID in ["71", "72", "73", "74", "75"]:
			arcpy.AddMessage("Calculating calorie requirement for female 35 - 39 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f3539 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f3539 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f3539 is " + str(pop))
			f3539 = (1.55 * (845.6 + 8.118 * kg5)) * pop
			arcpy.AddMessage("LLER for f3539 age group (total kcal/day): " + str(f3539))
			LLER += f3539
			arcpy.AddMessage("Total LLER is: " + str(LLER))
		
		#The male 35-39 age group
		elif OID in ["76", "77", "78", "79", "80"]:
			arcpy.AddMessage("Calculating calorie requirement for male 35 - 39 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m3539 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m3539 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m3539 is " + str(pop))
			m3539 = (1.55 * (873.1 + 11.472 * kg5)) * pop
			arcpy.AddMessage("LLER for m3539 age group (total kcal/day): " + str(m3539))
			LLER += m3539
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 40-44 age group
		elif OID in ["81", "82", "83", "84", "85"]:
			arcpy.AddMessage("Calculating calorie requirement for female 40 - 44 age group.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f4044 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f4044 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f4044 is " + str(pop))
			f4044 = (1.55 * (845.6 + 8.118 * kg5)) * pop
			arcpy.AddMessage("LLER for f4044 age group (total kcal/day): " + str(f4044))
			LLER += f4044
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 40-44 age group
		elif OID in ["86", "87", "88", "89", "90"]:
			arcpy.AddMessage("Calculating calorie requirement for male 40 - 44 age group.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m4044 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m4044 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m4044 is " + str(pop))
			m4044 = (1.55 * (873.1 + 11.472 * kg5)) * pop
			arcpy.AddMessage("LLER for m4044 age group (total kcal/day): " + str(m4044))
			LLER += m4044
			arcpy.AddMessage("Total LLER is " + str(LLER))
			
		#The female 45-49 age group
		elif OID in ["91", "92", "93", "94", "95"]:
			arcpy.AddMessage("Calculating calorie requirement for female 45 - 49.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f4549 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f4549 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f4549 is " + str(pop))
			f4549 = (1.55 * (845.6 + 8.118 * kg5)) * pop
			arcpy.AddMessage("LLER for f4549 age group (total kcal/day): " + str(f4549))
			LLER += f4549
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 45-49 age group
		elif OID in ["96", "97", "98", "99", "100"]:
			arcpy.AddMessage("Calculating calorie requirement for male 45 - 49.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m4549 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m4549 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m4549 is " + str(pop))
			m4549 = (1.55 * (873.1 + 11.472 * kg5)) * pop
			arcpy.AddMessage("LLER for m4549 age group (total kcal/day): " + str(m4549))
			LLER += m4549
			arcpy.AddMessage("Total LLER is " + str(LLER))
			
		#The female 50-54 age group
		elif OID in ["101", "102", "103", "104", "105"]:
			arcpy.AddMessage("Calculating calorie requirement for female 50 - 54.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f5054 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f5054 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f5054 is " + str(pop))
			f5054 = (1.55 * (845.6 + 8.118 * kg5)) * pop
			arcpy.AddMessage("LLER for f5054 age group (total kcal/day): " + str(f5054))
			LLER += f5054
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 50-54 age group
		elif OID in ["106", "107", "108", "109", "110"]:
			arcpy.AddMessage("Calculating calorie requirement for male 50 - 54.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m5054 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m5054 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m5054 is " + str(pop))
			m5054 = (1.55 * (873.1 + 11.472 * kg5)) * pop
			arcpy.AddMessage("LLER for m5054 age group (total kcal/day): " + str(m5054))
			LLER += m5054
			arcpy.AddMessage("Total LLER is " + str(LLER))
			
		#The female 55-59 age group
		elif OID in ["111", "112", "113", "114", "115"]:
			arcpy.AddMessage("Calculating calorie requirement for female 55 - 59.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f5559 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f5559 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f5559 is " + str(pop))
			f5559 = (1.55 * (845.6 + 8.118 * kg5)) * pop
			arcpy.AddMessage("LLER for f5559 age group (total kcal/day): " + str(f5559))
			LLER += f5559
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 55-59 age group
		elif OID in ["116", "117", "118", "119", "120"]:
			arcpy.AddMessage("Calculating calorie requirement for male 55 - 59.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m5559 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m5559 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m5559 is " + str(pop))
			m5559 = (1.55 * (873.1 + 11.472 * kg5)) * pop
			arcpy.AddMessage("LLER for m5559 age group (total kcal/day): " + str(m5559))
			LLER += m5559
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 60-64 age group
		elif OID in ["121", "122", "123", "124", "125"]:
			arcpy.AddMessage("Calculating calorie requirement for female 60 - 64.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f6064 is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f6064 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f6064 is " + str(pop))
			f6064 = (1.55 * (658.5 + 9.082 * kg5)) * pop
			arcpy.AddMessage("LLER for f6064 age group (total kcal/day): " + str(f6064))
			LLER += f6064
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 60-64 age group
		elif OID in ["126", "127", "128", "129", "130"]:
			arcpy.AddMessage("Calculating calorie requirement for male 60 - 64.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m6064 is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m6064 is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m6064 is " + str(pop))
			m6064 = (1.55 * (587.7 + 11.711 * kg5)) * pop
			arcpy.AddMessage("LLER for m6064 age group (total kcal/day): " + str(m6064))
			LLER += m6064
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The female 65+ age group
		elif OID in ["131", "132", "133", "134", "135"]:
			arcpy.AddMessage("Calculating calorie requirement for female 65+.")
			height = (femaleStatureInt / 161.8) * 163.3383
			arcpy.AddMessage("female height for f65+ is " + str(height))
			kg5 = 17.38 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for f65+ is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for f65+ is " + str(pop))
			f65pl = (1.55 * (658.5 + 9.082 * kg5)) * pop
			arcpy.AddMessage("LLER for f65pl age group (total kcal/day): " + str(f65pl))
			LLER += f65pl
			arcpy.AddMessage("Total LLER is: " + str(LLER))
			
		#The male 65+ age group
		elif OID in ["136", "137", "138", "139", "140"]:
			arcpy.AddMessage("Calculating calorie requirement fo male 65+.")
			height = (maleStatureInt / 175.7) * 176.8492
			arcpy.AddMessage("male height for m65+ is " + str(height))
			kg5 = 18.66 * ((height / 100)**2)
			arcpy.AddMessage("kg5 for m65+ is " + str(kg5))
			array = arcpy.RasterToNumPyArray(r)
			pop = array.sum()
			arcpy.AddMessage("population for m65+ is " + str(pop))
			m65pl = (1.55 * (587.7 + 11.711 * kg5)) * pop
			arcpy.AddMessage("LLER for m65pl age group (total kcal/day): " + str(m65pl))
			LLER += m65pl
			arcpy.AddMessage("Total LLER is: " + str(LLER))	
			
		else:
			arcpy.AddMessage("Age group and/or Year for " + str(OID) + " does not exist")
	
	
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