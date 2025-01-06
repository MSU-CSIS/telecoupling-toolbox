# Created on: 2017-06-23 01:46:39.0000
# Usage: Calculate population density
#----------------------------------------------------------------------------------------------------------------

# Import all necessary module dependencies
import arcpy
import os
import sys
import datetime
import string
import arcpy.mapping

arcpy.env.overwriteOutput = True
#arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def autoIncrement(pInterval = 1):
	global rec
	rec = rec + pInterval
	return rec

def PopCountDensity(inFeature, featureField, inCensus, censusField, outFC, index):

	try:
		### Initialization
		# Start the timer
		startDateTime1 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		arcpy.AddMessage(startDateTime1 + " setting up environment variables.")

		#Begin calculating population density
		#Create an index value to keep track of intermediate outputs and fieldnames
		arcpy.AddMessage("Calculating population density...")
		
		#Perform population density caculation for first (only?) population feature class
		#If the user specified an index, add an underscore as prefix
		if index != "":
			index = "_" + index
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
		arcpy.AddMessage("Calculating population density...")
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

		#If there is only one time point (ie, the POPCHG box in the GUI is not checked), run the next block of code
		#and output the feature class as the final shapefile.
		if index == "":
			#Output written to disk
			result = arcpy.FeatureClassToFeatureClass_conversion(os.path.join(arcpy.env.scratchGDB, tempName), os.path.dirname(outFC), os.path.basename(outFC), "", fieldMappings)
			#Layer feature is created so that the result automatically displays in viewer once tool successfully runs
			makeLayer = arcpy.MakeFeatureLayer_management(result, os.path.join(arcpy.env.scratchGDB, "FC_layer"))
			lyr = makeLayer.getOutput(0)
			mxd = arcpy.mapping.MapDocument("CURRENT")
			dataframes = arcpy.mapping.ListDataFrames(mxd)[0]
			arcpy.mapping.AddLayer(dataframes, lyr, "TOP")

		#If there are two time points (ie, the POPCHG box in the GUI is checked), run this elif statement
		#The elif statement will save timepoint 1 to the scratch geodatabase.
		elif index == "_1":
			arcpy.FeatureClassToFeatureClass_conversion(os.path.join(arcpy.env.scratchGDB, tempName), os.path.join(arcpy.env.scratchGDB), os.path.join(tempName_1), "", fieldMappings)
			arcpy.AddMessage("Beginning the second time point.")

		#If there are two time points (ie, the POPCHG box in the GUI is checked), run this else statement
		#The first step in the else statement is to find a field that will be used to join the two time points.
		else:
			tempName_2 = "PopDens_2"
			arcpy.FeatureClassToFeatureClass_conversion(os.path.join(arcpy.env.scratchGDB, tempName), os.path.join(arcpy.env.scratchGDB), os.path.join(tempName_2), "", fieldMappings)
			
			#Look to see if a field of OID type exists for the first time point feature class
			type_1 = arcpy.ListFields(os.path.join(arcpy.env.scratchGDB, tempName_1))
			for field in type_1:
				if field.type == "OID":
					OID_1 = field.name
					break
				else:
					OID_1 = ""

			#Look tosee if a field of OID type exists for the second time point feature class
			type_2 = arcpy.ListFields(os.path.join(arcpy.env.scratchGDB, tempName_2))
			for field in type_2:
				if field.type == "OID":
					OID_2 = field.name
					break
				else:
					OID_2 = ""

			#If both time points contain a field of OID type, then join the two feature classes using this field
			if OID_1 != "" and OID_2 != "":
				arcpy.AddMessage("Joining first and second time point.")
				arcpy.JoinField_management(os.path.join(arcpy.env.scratchGDB, tempName_1), OID_1, os.path.join(arcpy.env.scratchGDB, tempName_2), OID_2, retainList)

				#Calculate the change in population between the two time points
				arcpy.AddField_management(os.path.join(arcpy.env.scratchGDB, tempName_1), "PopGrowth", "DOUBLE")
				with arcpy.da.UpdateCursor(os.path.join(arcpy.env.scratchGDB, tempName_1), ("PopGrowth", "popCount_1", "popCount_2")) as cursor:
					for row in cursor:
						row[0] = ((row[2] - row[1]) / row[1]) * 100
						cursor.updateRow(row)

				#Remove all but the desired fields
				retainList = ["popCount_1", "AREAKM2", "popDens_1", "popCount_2", "popDens_2", "PopGrowth"]
				fieldMappings = arcpy.FieldMappings()
				fieldMappings.addTable(os.path.join(arcpy.env.scratchGDB, tempName_1))
				for fld in fieldMappings.fields:
					if fld.name not in retainList:
						fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(fld.name))

				#Output written to disk
				result = arcpy.FeatureClassToFeatureClass_conversion(os.path.join(arcpy.env.scratchGDB, tempName_1), os.path.dirname(outFC), os.path.basename(outFC), "", fieldMappings)

				#Layer feature is created so that the result automatically displays in viewer once tool successfully runs
				makeLayer = arcpy.MakeFeatureLayer_management(result, os.path.join(arcpy.env.scratchGDB, "FC_layer"))
				lyr = makeLayer.getOutput(0)
				mxd = arcpy.mapping.MapDocument("CURRENT")
				dataframes = arcpy.mapping.ListDataFrames(mxd)[0]
				arcpy.mapping.AddLayer(dataframes, lyr, "TOP")

			#If at least one of the time points did not contain a field of OID type, then a new field will be added to both time points.
			#This field will be used to join the two feature classes.
			else:
				iterateList = [os.path.join(arcpy.env.scratchGDB, tempName_1), os.path.join(arcpy.env.scratchGDB, tempName_2)]
				
				#Add a field of unique IDs to both time points.
				for i in iterateList:
					if i == iterateList[0]:
						arcpy.AddField_management(i, "join_field", "LONG") 
						with arcpy.da.UpdateCursor(iterateList[0], "join_field") as cursor:
							for row in cursor:
								row[0] = autoIncrement()
								cursor.updateRow(row) 
							del cursor 			
					else:
						arcpy.AddField_management(i, "join_field", "LONG")
						rec = 0
						with arcpy.da.UpdateCursor(iterateList[-1], "join_field") as cursor:
							for row in cursor:
								row[0] = autoIncrement()
								cursor.updateRow(row) 
							del cursor

				#Join the two time points using the newly created field
				arcpy.AddMessage("Joining first and second time point.")
				arcpy.JoinField_management(os.path.join(arcpy.env.scratchGDB, tempName_1), "join_field", os.path.join(arcpy.env.scratchGDB, tempName_2), "join_field")

				#Calculate the change in population between the two time points
				arcpy.AddField_management(os.path.join(arcpy.env.scratchGDB, tempName_1), "PopGrowth", "DOUBLE")
				with arcpy.da.UpdateCursor(os.path.join(arcpy.env.scratchGDB, tempName_1), ("PopGrowth", "popCount_1", "popCount_2")) as cursor:
					for row in cursor:
						row[0] = ((row[2] - row[1]) / row[1]) * 100
						cursor.updateRow(row)
				
				#Remove all but te desired fields
				retainList = ["popCount_1", "AREAKM2", "popDens_1", "popCount_2", "popDens_2", "PopGrowth"]
				fieldMappings = arcpy.FieldMappings()
				fieldMappings.addTable(os.path.join(arcpy.env.scratchGDB, tempName_1))
				for fld in fieldMappings.fields:
					if fld.name not in retainList:
						fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(fld.name))

				#Output written to disk
				result = arcpy.FeatureClassToFeatureClass_conversion(os.path.join(arcpy.env.scratchGDB, tempName_1), os.path.dirname(outFC), os.path.basename(outFC), "", fieldMappings)

				#Layer feature is created so that the result automatically displays in viewer once tool successfully runs
				makeLayer = arcpy.MakeFeatureLayer_management(result, os.path.join(arcpy.env.scratchGDB, "FC_layer"))
				lyr = makeLayer.getOutput(0)
				mxd = arcpy.mapping.MapDocument("CURRENT")
				dataframes = arcpy.mapping.ListDataFrames(mxd)[0]
				arcpy.mapping.AddLayer(dataframes, lyr, "TOP")

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

if __name__ == '__main__':
	#Get the values of the input parameters
	inFeature = arcpy.GetParameterAsText(0)
	featureField = arcpy.GetParameterAsText(1)
	inCensus = arcpy.GetParameterAsText(2)
	censusField = arcpy.GetParameterAsText(3)
	outFC = arcpy.GetParameterAsText(4)
	isChecked_PopChg = arcpy.GetParameterAsText(5)
	inCensusT2 = arcpy.GetParameterAsText(6)
	censusFieldT2 = arcpy.GetParameterAsText(7)

	#Create an index value to keep track of intermediate outputs and fieldnames.
	index = ""
	rec = 0
	
	#Iterate through the PopCountDensity() function according to whether POPCHG was checked in the GUI.
	if string.upper(str(isChecked_PopChg)) == "TRUE":
		index = "1"
		tempName_1 = "PopDens_1"
		PopCountDensity(inFeature, featureField, inCensus, censusField, tempName_1, index)
		index = "2"
		PopCountDensity(inFeature, featureField, inCensusT2, censusFieldT2, outFC, index)
	else:
		PopCountDensity(inFeature, featureField, inCensus, censusField, outFC, index)
