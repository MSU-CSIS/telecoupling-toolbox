# Created on: 2017-06-23 01:46:39.0000
# Usage: Calculate population density
#----------------------------------------------------------------------------------------------------------------

# Import all necessary module dependencies
import arcpy, os, sys, zipfile, shutil

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def unZipFile(inFile, dir_name):
	#Create a folder in the directory to extract zip to 
	zipFolder = os.path.join(arcpy.env.scratchFolder, dir_name)  
	# Extract the zip contents
	zip2Extract = zipfile.ZipFile(inFile, 'r')	
	zip2Extract.extractall(zipFolder)
	zip2Extract.close() 
	return

def PopCountDensity(inFeature, featureField, inCensus, censusField, index):
    	
	try:

		#Begin calculating population density
		#Create an index value to keep track of intermediate outputs and fieldnames
		arcpy.AddMessage("Calculating population density...")

		#Create a copy of the census feature class that we can add new fields to for calculations.
		#This is more appropriate than altering the user's input data.
		fieldMappings = arcpy.FieldMappings()
		fieldMappings.addTable(inCensus)
		[fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(aFld.name)) for aFld in fieldMappings.fields if aFld.name != censusField]

		desc = arcpy.Describe(inCensus)
		tempName = "CensusFeature_%s%s" % (desc.baseName, index)
		inCensus = arcpy.FeatureClassToFeatureClass_conversion(inCensus, arcpy.env.scratchGDB, tempName, "", fieldMappings)

		#Add and populate the area field to the Census Feature
		arcpy.AddField_management(inCensus, "popArea", "DOUBLE")
		with arcpy.da.UpdateCursor(inCensus, ['SHAPE@AREA', 'popArea']) as cursor:
			for row in cursor:
				row[1] = row[0] / 1E6
				cursor.updateRow(row)

		#Calculate the population density
		arcpy.AddField_management(inCensus, "popDens" + index, "DOUBLE")
		with arcpy.da.UpdateCursor(inCensus, ('popDens' + index, censusField, 'popArea')) as cursor:
			for row in cursor:
				row[0] = row[1] / row[2]
				cursor.updateRow(row)

		#Intersect the reporting units with the population features.
		tempName = "IntersectTEST2_%s%s" % (desc.baseName, index)
		intersectOutput = arcpy.Intersect_analysis([inFeature,inCensus], os.path.join(arcpy.env.scratchGDB, tempName)) 

		#Add and populate the area field of the intersected polygons 
		arcpy.AddField_management(intersectOutput, "intArea", "DOUBLE")
		with arcpy.da.UpdateCursor(intersectOutput, ['SHAPE@AREA', 'intArea']) as cursor:
			for row in cursor:
				row[1] = row[0] / 1E6
				cursor.updateRow(row)

		#Calculate the population of the itersected areas by multiplying population density by intersected area
		#Set up a calculation expression for the density calculation
		pd_name = "popDens" + index
		#Calculate the population density for the intersected areas
		arcpy.AddField_management(intersectOutput, "popCount", "DOUBLE")
		with arcpy.da.UpdateCursor(intersectOutput, ('popCount', pd_name, 'intArea')) as cursor:
			for row in cursor:
				row[0] = row[1] * row[2]
				cursor.updateRow(row)

		#Dissolve the feature by the featureField (specified by the user)
		tempName = "Dissolve%s" % (index)
		arcpy.AddMessage("Dissolving the Feature Class by featureField.")
		dissolve = arcpy.Dissolve_management(intersectOutput, os.path.join(arcpy.env.scratchGDB, tempName), featureField, "intArea SUM;popCount SUM", "MULTI_PART")

		#Rename the fields that hold information on population and feature area
		#Create variable to hold population information
		pc_name = "popCount" + index
		fieldList = arcpy.ListFields(dissolve)
		for field in fieldList:
			if "sum_pop" in field.name.lower():
				popVar = field.name
				popVar.encode('ascii', 'ignore')
				arcpy.AddField_management(os.path.join(arcpy.env.scratchGDB, tempName), pc_name, "DOUBLE")
				with arcpy.da.UpdateCursor(os.path.join(arcpy.env.scratchGDB, tempName), (pc_name, popVar)) as cursor:
					for row in cursor:
						row[0] = row[1]
						cursor.updateRow(row)
				arcpy.DeleteField_management(os.path.join(arcpy.env.scratchGDB, tempName), popVar)

		#Create variable to hold area information
		area_name = "AREAKM2"
		for field in fieldList:
			if "sum_int" in field.name.lower():
				areaVar = field.name
				areaVar.encode('ascii', 'ignore')
				arcpy.AddField_management(os.path.join(arcpy.env.scratchGDB, tempName), area_name, "DOUBLE")
				with arcpy.da.UpdateCursor(os.path.join(arcpy.env.scratchGDB, tempName), (area_name, areaVar)) as cursor:
					for row in cursor:
						row[0] = row[1]
						cursor.updateRow(row)
				arcpy.DeleteField_management(os.path.join(arcpy.env.scratchGDB, tempName), areaVar)

		#Calculate the population density
		popDens = "popDens" + index
		arcpy.AddField_management(os.path.join(arcpy.env.scratchGDB, tempName), popDens, "DOUBLE")
		with arcpy.da.UpdateCursor(os.path.join(arcpy.env.scratchGDB, tempName), (popDens, pc_name, area_name)) as cursor:
			for row in cursor:
				row[0] = row[1] / row[2]
				cursor.updateRow(row)     
		
		#Remove all but the desired fields
		retainList = [pc_name, area_name, popDens]
		fieldMappings = arcpy.FieldMappings()
		fieldMappings.addTable(os.path.join(arcpy.env.scratchGDB, tempName))
		for fld in fieldMappings.fields:
			if fld.name not in retainList:
				fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(fld.name))

		#Run the next block of code
		#and output the feature class as the final shapefile.
		#Output written to disk
		result = arcpy.CopyFeatures_management(os.path.join(arcpy.env.scratchGDB, tempName), os.path.join(arcpy.env.scratchGDB, "PopMetrics"))
		
		#result = arcpy.FeatureClassToFeatureClass_conversion(os.path.join(arcpy.env.scratchGDB, tempName), arcpy.env.scratchGDB, os.path.basename(outFC), "", fieldMappings)
		#Layer feature is created so that the result automatically displays in viewer once tool successfully runs
		out_fl = arcpy.MakeFeatureLayer_management(result, os.path.join(arcpy.env.scratchGDB, "fl_pop"))
		
		# Execute FeatureClassToGeodatabase
		arcpy.AddMessage("Converting Feature Class to Shapefile...")
		arcpy.FeatureClassToShapefile_conversion(os.path.join(arcpy.env.scratchGDB, "PopMetrics"), arcpy.env.scratchFolder)

		### Create output maps zipped file ###
		arcpy.AddMessage("Creating output zipped folder with all output...")
		files = [os.path.join(arcpy.env.scratchFolder, file) for file in os.listdir(arcpy.env.scratchFolder) if os.path.isfile(os.path.join(arcpy.env.scratchFolder, file))]
		#create zipfile object as speficify 'w' for 'write' mode
		myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
		# LOOP through the file list and add to the zip file
		for zip_file in files:
			myzip.write(zip_file, os.path.basename(zip_file), compress_type=zipfile.ZIP_DEFLATED)

	
		### Set Parameters ####
		arcpy.SetParameter(4, out_fl)
		arcpy.SetParameter(5, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))
										  
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

if __name__ == '__main__':

	#Get the values of the input parameters
	inFeature_zip = arcpy.GetParameterAsText(0)
	featureField = arcpy.GetParameterAsText(1)
	inCensus_zip = arcpy.GetParameterAsText(2)
	censusField = arcpy.GetParameterAsText(3)

	#Unzip input feature shapefile
	arcpy.AddMessage("Unzipping Feature Shapefile ...")
	unZipFile(inFeature_zip, "inFeature")
	#the following block is necessary b/c the remote server changes uploaded zip name randomly
	#in order to retrieve the actual shp file name, list files inside unzipped folder
	inFeature_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "inFeature"))
	for file in inFeature_dir:
		if file.endswith(".shp"):
			inFeature_shp_name = file
	inFeature = os.path.join(arcpy.env.scratchFolder, "inFeature", inFeature_shp_name)

	#Unzip census feature shapefile
	arcpy.AddMessage("Unzipping Census Unit Shapefile ...")
	unZipFile(inCensus_zip, "inCensus")
	#the following block is necessary b/c the remote server changes uploaded zip name randomly
	#in order to retrieve the actual shp file name, list files inside unzipped folder
	inCensus_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "inCensus"))
	for file in inCensus_dir:
		if file.endswith(".shp"):
			inCensus_shp_name = file
	inCensus = os.path.join(arcpy.env.scratchFolder, "inCensus", inCensus_shp_name)

	#Run main function to calculate density and count
	PopCountDensity(inFeature, featureField, inCensus, censusField, "")
