import arcpy
from bs4 import BeautifulSoup
import sys, os, zipfile

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)
	
def AddMediaFlows():

	# Local variable:
	out_layer_src_fl = "source_lyr"
	out_view_tbl = "layer_view"
	out_layer_pnt_fc = r"in_memory\country_lyr"
	out_media_flows_fc = r"in_memory\media_lyr"
	out_merged_flows_fc = r"in_memory\merged_lyr"
	out_name_merge_fl = "Merged Media Flows"
	out_name_fl = "Media Flows"


	try:

		### 1. Create temp feature layer from source point and add XY coordinates ###
		# Process: Make Feature Layer (temporary)
		arcpy.AddMessage('Creating Feature Layer from Source Point ...')
		arcpy.SetProgressorLabel('Creating Feature Layer from Source Point ...')
		arcpy.MakeFeatureLayer_management(in_features=source_FeatureSet, out_layer=out_layer_src_fl)
		#### Add XY Coordinates To Point Layer ####
		arcpy.AddMessage('Adding XY Coordinates to Source Point Layer ...')
		arcpy.SetProgressorLabel('Adding XY Coordinates to Source Point Layer ...')
		arcpy.AddXY_management(out_layer_src_fl)

		### 2. The user should only add a single source location. If so, then store the XY coordinate values into a list object ###
		countRows = int(arcpy.GetCount_management(out_layer_src_fl).getOutput(0))

		if countRows > 1:
			arcpy.AddError("ERROR: You need to specify ONLY ONE source location on the map!!")
			raise arcpy.ExecuteError
		else:
			with arcpy.da.SearchCursor(out_layer_src_fl, ['POINT_X', 'POINT_Y']) as cursor:
				for row in cursor:
					srcPnt_XY = [row[0], row[1]]
			del cursor

		### 3. Create List of Strings Based on Selected Input Feature Layer Field ###
		fNames_lst = []
		# Search Cursor: the following only works with ArcGIS 10.1+ ###
		arcpy.SetProgressorLabel('Creating List of Values From Chosen Input Feature Layer Field ...')
		arcpy.AddMessage('Creating List of Values From Chosen Input Feature Layer Field ...')
		with arcpy.da.SearchCursor(input_fc, input_fc_field) as cursor:
			for row in cursor:
				fNames_lst.append(row[0])
		del cursor

		### 4. Read HTML input report file and parse its content grabbing desired tags ###
		arcpy.SetProgressorLabel('Reading and Parsing HTML File ...')
		arcpy.AddMessage('Reading and Parsing HTML File ...')
		soup = BeautifulSoup(open(input_html),'html.parser')
		links_geo = soup.find_all(lambda tag: tag.name == 'p' and tag.get('class') == ['c1'])
		#links_p = soup.find_all('p')
		text_elements_geo = [links_geo[i].find_all(text=True) for i in range(len(links_geo))]

		### 5. Initialize a dictionary to store frequency of geographic locations to be mapped: ###
		### Keys ---> unique values of the selected input feature field;
		### Values ---> count frequency of word match between parsed HTML string and dictionary key (e.g. country name) ###
		#country_parse = {k: None for k in country_lst}
		arcpy.SetProgressorLabel('Creating Dictionary with Frequency Counts of Geographic Locations from Parsed HTML ...')
		arcpy.AddMessage('Creating Dictionary with Frequency Counts of Geographic Locations from Parsed HTML ...')
		country_parse = {}
		for el in text_elements_geo:
			for geo in fNames_lst:
				if len(el) == 1 and geo in el[0]:
					if not geo in country_parse:
						country_parse[geo] = 1
					else:
						country_parse[geo] += 1
						
		### 6. Create a temporary point layer from the input Polygon feature class ###
		arcpy.SetProgressorLabel('Creating Temporary Point Layer from Input Feature Layer ...')
		arcpy.AddMessage('Creating Temporary Point Layer from Input Feature Layer ...')
		### Process: Feature To Point Layer ###
		arcpy.FeatureToPoint_management(input_fc, out_layer_pnt_fc, "INSIDE")

		### 7. Add Fields Required as Input by the XY To Line GP tool ###
		arcpy.SetProgressorLabel('Adding New Field to Temporary Point Layer ...')
		arcpy.AddMessage('Adding New Field to Temporary Point Layer ...')
		#### Add Fields to temporary feature layer ###
		arcpy.AddField_management(in_table=out_layer_pnt_fc, field_name="FROM_X", field_type="DOUBLE")
		arcpy.AddField_management(in_table=out_layer_pnt_fc, field_name="FROM_Y", field_type="DOUBLE")
		arcpy.AddField_management(in_table=out_layer_pnt_fc, field_name="TO_X", field_type="DOUBLE")
		arcpy.AddField_management(in_table=out_layer_pnt_fc, field_name="TO_Y", field_type="DOUBLE")
		arcpy.AddField_management(in_table=out_layer_pnt_fc, field_name="Frequency", field_type="SHORT")
		#### Add XY Coordinates To Point Layer ####
		arcpy.AddXY_management(out_layer_pnt_fc)

		### 8. Fill Out Values for All Newly Added Fields in the Temp Point Feature Layer ###
		arcpy.SetProgressorLabel('Transferring Values from Dictionary to Temporary Point Feature Layer ...')
		arcpy.AddMessage('Transferring Values from Dictionary to Temporary Point Feature Layer ...')
		fields_selection = ['FROM_X', 'FROM_Y', input_fc_field, 'TO_X', 'TO_Y', 'POINT_X', 'POINT_Y', 'Frequency']
		with arcpy.da.UpdateCursor(out_layer_pnt_fc, fields_selection) as cursor:
			for row in cursor:
				if row[2] in country_parse.keys():
					row[0] = srcPnt_XY[0]
					row[1] = srcPnt_XY[1]
					row[3] = row[5]
					row[4] = row[6]
					row[7] = country_parse[row[2]]
					# Update the cursor with the updated list
					cursor.updateRow(row)
				else:
					cursor.deleteRow()
		del cursor

		### 9. Remove Unnecessary Fields From the Temp Point Feature Layer ###
		arcpy.SetProgressorLabel('Removing Unnecessary Fields from Temporary Point Feature Layer ...')
		arcpy.AddMessage('Removing Unnecessary Fields from Temporary Point Feature Layer ...')
		fields = arcpy.ListFields(out_layer_pnt_fc)
		keepFields = ['FROM_X', 'FROM_Y', 'TO_X', 'TO_Y', 'Frequency']
		dropFields = [f.name for f in fields if f.name not in keepFields and f.type != 'OID' and f.type != 'Geometry']
		# delete fields
		arcpy.DeleteField_management(out_layer_pnt_fc, dropFields)

		### 10. Export temp feature class to CSV and use to draw flow lines ###
		arcpy.SetProgressorLabel('Creating Table View from Temporary Feature Layer ...')
		arcpy.AddMessage('Creating Table View from Temporary Feature Layer ...')
		arcpy.MakeTableView_management(in_table=out_layer_pnt_fc, out_view=out_view_tbl)

		### 11. If Merging Box is Checked, Merge Temp Point Feature Class To Copy of Input Flow Layer ###
		if is_checked_table:
			arcpy.SetProgressorLabel('Creating Media Information Radial Flow Lines ...')
			arcpy.AddMessage('Creating Media Information Radial Flow Lines ...')
			arcpy.XYToLine_management(in_table=out_view_tbl, out_featureclass=out_media_flows_fc,
									  startx_field='FROM_X', starty_field='FROM_Y',
									  endx_field='TO_X', endy_field='TO_Y',
									  line_type=lineType_str, id_field='Frequency',
									  spatial_reference=out_layer_pnt_fc)
			
			arcpy.SetProgressorLabel('Merging Media Information Flows With Existing Flow Layer ...')
			arcpy.AddMessage('Merging Media Information Flows With Existing Flow Layer ...')
			arcpy.Merge_management([out_media_flows_fc, input_flow_lyr], out_merged_flows_fc)
			# Process: Create a feature layer from the joined feature class to send back as output to GP tools
			out_fl = arcpy.MakeFeatureLayer_management(out_merged_flows_fc, out_name_merge_fl)
			# Execute FeatureClassToGeodatabase
			arcpy.AddMessage("Converting Feature Class to Shapefile...")
			arcpy.FeatureClassToShapefile_conversion(out_merged_flows_fc, arcpy.env.scratchFolder)			
		else:
			arcpy.SetProgressorLabel('Creating Media Information Radial Flow Lines ...')
			arcpy.AddMessage('Creating Media Information Radial Flow Lines ...')
			arcpy.XYToLine_management(in_table=out_view_tbl, out_featureclass=out_media_flows_fc,
									  startx_field='FROM_X', starty_field='FROM_Y',
									  endx_field='TO_X', endy_field='TO_Y',
									  line_type=lineType_str, id_field='Frequency',
									  spatial_reference=out_layer_pnt_fc)
			# Process: Create a feature layer from the joined feature class to send back as output to GP tools
			out_fl = arcpy.MakeFeatureLayer_management(out_media_flows_fc, out_name_fl) 
			# Execute FeatureClassToGeodatabase
			arcpy.AddMessage("Converting Feature Class to Shapefile...")
			arcpy.FeatureClassToShapefile_conversion(out_media_flows_fc, arcpy.env.scratchFolder)			
		
		arcpy.SetParameter(7, out_fl)			
		arcpy.ResetProgressor()
		
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
		
	arcpy.SetParameter(8, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))
	
if __name__ == '__main__':
	# Get the value of the input parameter
	input_fc = arcpy.GetParameterAsText(0)
	input_fc_field = arcpy.GetParameterAsText(1)
	input_html = arcpy.GetParameterAsText(2)
	source_FeatureSet = arcpy.GetParameterAsText(3)
	is_checked_table = arcpy.GetParameter(4)
	input_flow_lyr = arcpy.GetParameterAsText(5)
	lineType_str = arcpy.GetParameterAsText(6)

	#run add media flows method
	AddMediaFlows()

	#create zipfile output
	create_zip()
