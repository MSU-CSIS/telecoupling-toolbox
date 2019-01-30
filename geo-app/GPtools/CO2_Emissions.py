import arcpy
import sys, os, math, csv, zipfile

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

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
	f = open(output, 'wb')
	outWriter = csv.writer(f, dialect='excel')

	excludeTypes = ['Geometry', 'OID']
	excludeTypes = []
	fields = ExcludeFields(fc, excludeTypes)

	# Create Search Cursor: the following only works with ArcGIS 10.1+
	with arcpy.da.SearchCursor(fc, fields) as cursor:
		outWriter.writerow(cursor.fields)
		for row in cursor:
			row = [v.decode('utf8') if isinstance(v, str) else v for v in row]
			outWriter.writerow([unicode(s).encode("utf-8") for s in row])
	del row, cursor

	# Close opened file
	f.close()

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
			if id_field and flow_units:
				arcpy.XYToLine_management(in_table=inTable, out_featureclass=out_flows_fc,
										  startx_field=startX_field, starty_field=startY_field,
										  endx_field=endX_field, endy_field=endY_field,
										  line_type=lineType_str, id_field=id_field, spatial_reference=spRef)

				arcpy.CopyRows_management(inTable, out_tbl)
				## JOIN output flows with attribute from input table
				arcpy.JoinField_management(out_flows_fc, id_field, out_tbl, id_field, flow_units)   

		except Exception:
			e = sys.exc_info()[1]
			arcpy.AddError('An error occurred: {}'.format(e.args[0]))

	return out_flows_fc
	
def calc_CO2_emissions(flows_lyr):

	# Local variable:
	out_flows_CO2_fc = os.path.join(arcpy.env.scratchGDB, "CO2Emissions_fc")
	out_CO2_Name = "CO2 Emissions"	

	try:
		#Create feature class from copy of input feature layer 
		arcpy.AddMessage('Creating Feature Class from Input Feature Layer ...')
		arcpy.SetProgressorLabel('Creating Feature Class from Input Feature Layer ...')
		arcpy.CopyFeatures_management(flows_lyr, out_flows_CO2_fc)
				
		### ADD FIELD: creating new field to store CO2 total emission per trip ###
		arcpy.AddMessage('Adding CO2 Emission Field to Feature Class ...')
		arcpy.SetProgressorLabel('Adding CO2 Emission Field to Feature Class ...')
		# add new CO2 emission field
		arcpy.AddField_management(in_table=out_flows_CO2_fc, field_name="CO2_EMISSIONS_KG", field_type="LONG")

		### CALCULATE FIELD: creating new field to store CO2 total emission per trip ###
		arcpy.AddMessage('Calculating CO2 Emissions for Each Flow Line ...')
		arcpy.SetProgressorLabel('Calculating CO2 Emissions for Each Flow Line ...')
		tot_emissions = 0        
		## Is there a field in the input feature layer representing quantity of flows? 
		## If not, assign a default value == 1 to the flow as units.
		if flow_units != '':	
			#Check user input to make sure the transport units field specified matches one of the attributes of the inputFC
			fieldnames = [f.name for f in arcpy.ListFields(out_flows_CO2_fc)]
			if flow_units.capitalize() not in fieldnames and flow_units.upper() not in fieldnames:
				arcpy.AddError("ERROR: The chosen transportation units attribute does not exist in the input layer!")
				raise arcpy.ExecuteError
		   
			cursor = arcpy.da.UpdateCursor(out_flows_CO2_fc, ['SHAPE@LENGTH', fieldnames[fieldnames.index(flow_units)], 'CO2_EMISSIONS_KG'])
			for row in cursor:
				if row[1] is None or str(row[1]).upper() == "n/a" or str(row[1]).upper() == r"n\a" or str(row[1]).upper() == "NA":			
					continue 
				else:
					total_trips = math.ceil(float(row[1])/capacity_per_trip)
					#SHAPE@LENGTH will be likely in meters (depending on coordinate system)
					row[2] = row[0] * total_trips * CO2_emission
					tot_emissions += row[2]
					cursor.updateRow(row)
			
			#Export feature layer to CSV##
			arcpy.AddMessage('Exporting Flows CO2 Emissions Layer to CSV Table ...')
			outTable_CSV = os.path.join(arcpy.env.scratchFolder, "CO2_Emission_Table.csv")
			ExportToCSV(fc=out_flows_CO2_fc, output=outTable_CSV)			

		#arcpy.AddMessage('Writing Total Estimated CO2 to Output Report File ...')
		#arcpy.SetProgressorLabel('Writing Total Estimated CO2 to Output Report File ...')
		#out_txt = os.path.join(arcpy.env.scratchFolder,"CO2_Report.txt")	
		#file = open(out_txt,"w") 	
		#file.write("The current scenario produces a total estimated amount of released CO2 equal to: " + #str(tot_emissions) + " kilograms")		
		#file.close() 
		#arcpy.AddMessage("The current scenario produces a total estimated amount of released CO2 equal to: " + str(tot_emissions) + " kilograms")

		# Process: Create a feature layer from the joined feature class to send back as output to GP tools
		out_fl = arcpy.MakeFeatureLayer_management(out_flows_CO2_fc, out_CO2_Name)   

		# Execute FeatureClassToGeodatabase
		arcpy.AddMessage("Converting Feature Class to Shapefile...")
		arcpy.FeatureClassToShapefile_conversion(out_flows_CO2_fc, arcpy.env.scratchFolder)
		
		#### Set Parameters ####    
		arcpy.SetParameter(11, out_fl)
		#arcpy.SetParameter(5, out_txt)
		arcpy.SetParameter(12, outTable_CSV)

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
		
	arcpy.SetParameter(13, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))
		
if __name__ == '__main__':

	# Get the value of the input parameter
	arcpy.AddMessage("Reading input parameters...")
	inTable = arcpy.GetParameterAsText(0)
	startX_field = arcpy.GetParameterAsText(1)
	startY_field = arcpy.GetParameterAsText(2)
	endX_field = arcpy.GetParameterAsText(3)
	endY_field = arcpy.GetParameterAsText(4)
	id_field = arcpy.GetParameterAsText(5)
	flow_units = arcpy.GetParameterAsText(6)
	lineType_str = arcpy.GetParameterAsText(7)
	wkid = arcpy.GetParameter(8)
	# Field from input FC representing number of transportation units transferred
	capacity_per_trip = arcpy.GetParameter(9) # Transportation capacity (transport units per trip)
	CO2_emission = arcpy.GetParameter(10)  # Amount of CO2 emission (kg/unit)

	#calculate radial flows
	arcpy.AddMessage("Calculating radial flows...")
	rad_flow = DrawRadialFlows()

	#calculate CO2 emissions for the calculated radial flows
	arcpy.AddMessage("Calculating CO2 emissions on radial flows...")
	calc_CO2_emissions(rad_flow)

	#create zipfile output
	create_zip()