
# Esri start of added imports
import sys, os, arcpy
# Esri end of added imports

# Esri start of added variables
g_ESRI_variable_1 = u'D:\\data\\telecoupling-geoapp\\GPtools\\6SocioEconomic Analysis\\ToolData\\Nutrition Metrics\\AFR'
g_ESRI_variable_2 = u'D:\\data\\telecoupling-geoapp\\GPtools\\6SocioEconomic Analysis\\ToolData\\Nutrition Metrics\\Asia'
g_ESRI_variable_3 = u'D:\\data\\telecoupling-geoapp\\GPtools\\6SocioEconomic Analysis\\ToolData\\Nutrition Metrics\\LAC'
# Esri end of added variables

# Created on 2017-8-31
# Usage: Lower Limit of Energy Requirements (LLER) for area of interest.
#--------------------------------------------------------------------------------------------------------------

#Import all necessary module dependencies
import arcpy, numpy, csv, os, string, re, shutil, glob
from arcpy.sa import *

arcpy.env.overwriteOutput = True
#arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def Encode(x):
    """Encodes values into 'utf-8' format"""
    if isinstance(x, unicode):
        return x.encode("utf-8", 'ignore')
    else:
        return str(x)

def ExcludeFields(table, types=[]):
    """Return a list of fields minus those with specified field types"""
    fieldNames = []
    fds = arcpy.ListFields(table)
    for f in fds:
        if f.type not in types:
            fieldNames.append(f.name)
    return fieldNames

def ExportToCSV(fc, output):
    """Export Data to a CSV file"""
    # create the output writer
    outWriter = csv.writer(open(output, 'wb'), dialect='excel')

    excludeTypes = ['Geometry', 'OID']
    fields = ExcludeFields(fc, excludeTypes)

    # Create Search Cursor: the following only works with ArcGIS 10.1+
    with arcpy.da.SearchCursor(fc, fields) as cursor:
        outWriter.writerow(cursor.fields)
        for row in cursor:
            row = [v.decode('utf8') if isinstance(v, str) else v for v in row]
            outWriter.writerow([unicode(s).encode("utf-8") for s in row])
    del cursor

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

def rasterYearQuery(year, folder, ext):
	raster_lst = []
	try:
		for file in os.listdir(folder):
			if file.endswith(ext):
				if year in file:
					raster_lst.append(file)
				
	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))	
	except Exception as ex:
		arcpy.AddError(ex.args[0])
		
	return raster_lst

def clipRaster(rasterList, in_folder, out_folder, AOI):
	try:
		for r in rasterList:
			out_rasterName = r[:-4] + "_clip.img"
			outExtractByMask = ExtractByMask(os.path.join(in_folder, r), AOI)
			outExtractByMask.save(os.path.join(out_folder, out_rasterName))
	
	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))	
	except Exception as ex:
		arcpy.AddError(ex.args[0])	
		
	return
	
def nutritionMetrics(AOI, year, maleStature, femaleStature, rasterFolder):

	#Create intermediate folder where output will be temporarily saved
	int_directory = os.path.join(arcpy.env.scratchFolder, "intermediate")
	if not os.path.exists(int_directory):
		os.makedirs(int_directory)
	arcpy.AddMessage("Intermediate output folder created!")
	arcpy.AddMessage("Calculating nutrition metrics. This may take several minutes depending on size of AOI... ")
	
	#Subset rasters by the selected year of interest before clipping them by the AOI
	arcpy.AddMessage("Querying rasters for selected year:")	
	arcpy.AddMessage(year)	
	rasterYearList = rasterYearQuery(year, rasterFolder, ".tif")
	
	#Clip the rasters sub by the AOI
	arcpy.AddMessage("Clipping rasters by AOI...")	
	clipRaster(rasterYearList, rasterFolder, int_directory, AOI)
	
	#Loop through the exported rasters and calculate nutrition metrics for each rasters
	rasterList = []
	for file in os.listdir(int_directory):
		if file.endswith(".img"):
			rasterList.append(os.path.join(int_directory, file))
		
	#Calculate nutrition metrics
	LLER = 0    #This will keep the tally of 'Lower Limit of Energy Requirement' in kcal/day for the study area (AOI).
	groupList = []
	totalPop = 0    #This will keep the tally of total population in the study area (AOI).
	maleStatureInt = float(maleStature)
	femaleStatureInt = float(femaleStature)

	for r in rasterList:
				
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
		
	#Append the Nutrition Information to new feature class
	# Execute CreateFeatureclass
	out_name = "aoi_nutrition.shp"
	arcpy.AddMessage('Creating New Nutrition Feature Class ...')
	arcpy.CreateFeatureclass_management(int_directory, out_name, "POINT", spatial_reference=arcpy.SpatialReference(3857))
	aoi_nutrition = os.path.join(arcpy.env.scratchFolder, "intermediate", out_name)
	arcpy.AddMessage('Adding Fields to Nutrition Feature Class ...')
	arcpy.AddField_management(aoi_nutrition, "ageGroup", "TEXT")
	arcpy.AddField_management(aoi_nutrition, "Pop", "DOUBLE", "", 5)
	arcpy.AddField_management(aoi_nutrition, "LLER", "DOUBLE", "", 5)
	arcpy.AddField_management(aoi_nutrition, "LLER_pp", "DOUBLE", "", 5)
	arcpy.DeleteField_management(aoi_nutrition, "Id")

	#The list of values that are added to the final shapefile
	list = [("f0004", popf0004, nutf0004, nutf0004/popf0004), ("m0004", popm0004, nutm0004, nutm0004/popm0004), ("f0509", popf0509, nutf0509, nutf0509/popf0509), ("m0509", popm0509, nutm0509, nutm0509/popm0509), 
			("f1014", popf1014, nutf1014, nutf1014/popf1014), ("m1014", popm1014, nutm1014, nutm1014/popm1014), ("f1519", popf1519, nutf1519, nutf1519/popf1519), ("m1519", popm1519, nutm1519, nutm1519/popm1519), 
			("f2024", popf2024, nutf2024, nutf2024/popf2024), ("m2024", popm2024, nutm2024, nutm2024/popm2024), ("f2529", popf2529, nutf2529, nutf2529/popf2529), ("m2529", popm2529, nutm2529, nutm2529/popm2529), 
			("f3034", popf3034, nutf3034, nutf3034/popf3034), ("m3034", popm3034, nutm3034, nutm3034/popm3034), ("f3539", popf3539, nutf3539, nutf3539/popf3539), ("m3539", popm3539, nutm3539, nutm3539/popm3539), 
			("f4044", popf4044, nutf4044, nutf4044/popf4044), ("m4044", popm4044, nutm4044, nutm4044/popm4044), ("f4549", popf4549, nutf4549, nutf4549/popf4549), ("m4549", popm4549, nutm4549, nutm4549/popm4549), 
			("f5054", popf5054, nutf5054, nutf5054/popf5054), ("m5054", popm5054, nutm5054, nutm5054/popm5054), ("f5559", popf5559, nutf5559, nutf5559/popf5559), ("m5559", popm5559, nutm5559, nutm5559/popm5559), 
			("f6064", popf6064, nutf6064, nutf6064/popf6064), ("m6064", popm6064, nutm6064, nutm6064/popm6064), ("f65pl", popf65pl, nutf65pl, nutf65pl/popf65pl), ("m65pl", popm65pl, nutm65pl, nutm65pl/popm65pl), 
			("total", totalPop, LLER, LLER/totalPop)]

	arcpy.AddMessage('Populating Rows in Nutrition Feature Class ...')
	#Add values to Shapefile Attribute Table
	with arcpy.da.InsertCursor(aoi_nutrition, ("ageGroup", "Pop", "LLER", "LLER_pp")) as cursor:
		for row in list:
			cursor.insertRow(row)

	# Delete cursor object
	del cursor
			
	# Process: Export Data to CSV File
	arcpy.AddMessage('Exporting Feature Class Attributes to CSV ...')
	outTable_CSV = os.path.join(arcpy.env.scratchFolder, "Nutrition_Metrics.csv")
	ExportToCSV(fc=aoi_nutrition, output=outTable_CSV)

	#### Set Parameters ####
	arcpy.SetParameterAsText(5, outTable_CSV)		
			
			
if __name__ == '__main__':
    
	isLicensed()

	#Get the values of the input parameters
	AOI = arcpy.GetParameterAsText(0)
	continent = arcpy.GetParameterAsText(1)
	year = arcpy.GetParameterAsText(2)
	maleStature = arcpy.GetParameterAsText(3)
	femaleStature = arcpy.GetParameterAsText(4)
		
	#This is the path to the mosaic database with demographic information
	if continent == "Africa":
		rasterFolder = g_ESRI_variable_1
	elif continent == "Asia":
		rasterFolder = g_ESRI_variable_2
	else:
		rasterFolder = g_ESRI_variable_3

	arcpy.AddMessage("The Selected Continent is " + continent)
		
	#Run the Nutrition Metrics tool
	try:
		nutritionMetrics(AOI, year, maleStature, femaleStature, rasterFolder)
		
		#Remove the intermediate output folder
		arcpy.AddMessage("Removing Intermediate Output Folder ...")
		os.chdir("..")
		shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
	
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))



