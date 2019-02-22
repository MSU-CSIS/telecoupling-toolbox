# Import all necessary module dependencies
import arcpy
import os, sys, zipfile

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def DrawRadialFlows():

	# Try to assign the spatial reference by using the Well-Known ID for the input
	try:
		spRef = arcpy.SpatialReference(int(wkid))    
	except:
	# If the SR cannot be created, assume 4326
		arcpy.AddWarning("Problem creating the spatial reference!! Assumed to be WGS84 (wkid: 4326)")
		spRef = arcpy.SpatialReference(4326)
		
	# Local variable:
	out_flows_fc = r"in_memory\FlowsLineXY"
	out_tbl = r"in_memory\tmpTable"
	out_Name = "Telecoupling Flows"	

	if inTable and inTable != "#":

		try:
			# XY To Line
			arcpy.AddMessage('Creating Radial Flow Lines from Input File ...')
			arcpy.SetProgressorLabel('Creating Radial Flow Lines from Input File ...')
			if id_field and flow_amnt:
				arcpy.XYToLine_management(in_table=inTable, out_featureclass=out_flows_fc,
										  startx_field=startX_field, starty_field=startY_field,
										  endx_field=endX_field, endy_field=endY_field,
										  line_type=lineType_str, id_field=id_field, spatial_reference=spRef)

				arcpy.CopyRows_management(inTable, out_tbl)
				## JOIN output flows with attribute from input table
				arcpy.JoinField_management(out_flows_fc, id_field, out_tbl, id_field, flow_amnt)


			# Process: Create a feature layer from the joined feature class to send back as output to GP tools
			out_fl = arcpy.MakeFeatureLayer_management(out_flows_fc, out_Name)    

			# Send string of (derived) output parameters back to the tool
			arcpy.SetParameter(9, out_fl)

			# Execute FeatureClassToGeodatabase
			arcpy.AddMessage("Converting Feature Class to Shapefile...")
			arcpy.FeatureClassToShapefile_conversion(out_flows_fc, arcpy.env.scratchFolder)
		

		except Exception:
			e = sys.exc_info()[1]
			arcpy.AddError('An error occurred: {}'.format(e.args[0]))

def create_zip():
	try:
		### Create output maps zipped file ###
		arcpy.AddMessage("Creating output zipped folder with all output...")
		files = [os.path.join(arcpy.env.scratchFolder, file) for file in os.listdir(arcpy.env.scratchFolder) if (os.path.isfile(os.path.join(arcpy.env.scratchFolder, file)) and not file.endswith((".csv", ".xml")))]
		#create zipfile object as speficify 'w' for 'write' mode
		myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
		# LOOP through the file list and add to the zip file
		for zip_file in files:
			myzip.write(zip_file, os.path.basename(zip_file), compress_type=zipfile.ZIP_DEFLATED)	

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	arcpy.SetParameter(10, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))
	
	
if __name__ == '__main__':
	# Get the value of the input parameter
	inTable = arcpy.GetParameterAsText(0)
	startX_field = arcpy.GetParameterAsText(1)
	startY_field = arcpy.GetParameterAsText(2)
	endX_field = arcpy.GetParameterAsText(3)
	endY_field = arcpy.GetParameterAsText(4)
	id_field = arcpy.GetParameterAsText(5)
	flow_amnt = arcpy.GetParameterAsText(6)
	lineType_str = arcpy.GetParameterAsText(7)
	wkid = arcpy.GetParameter(8)

	#run draw flows method
	arcpy.AddMessage("Calculating radial flows...")
	DrawRadialFlows()

	#create zipfile output
	create_zip()