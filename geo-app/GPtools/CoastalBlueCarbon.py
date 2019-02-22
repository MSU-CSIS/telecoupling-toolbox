#Import all modules
import arcpy, os, sys, shutil, glob, zipfile
from arcpy.sa import *
import natcap.invest.coastal_blue_carbon.coastal_blue_carbon

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def isLicensed():
	"""Set whether tool is licensed to execute."""
	try:
		if arcpy.CheckExtension("Spatial") == "Available":
			arcpy.CheckOutExtension("Spatial")
		else:
			raise Exception
	except:
		return False
	return True

##Taken from https://www.calazan.com/how-to-zip-an-entire-directory-with-python/
def zip_folder(folder_path, output_path):
	"""Zip the contents of an entire folder (with that folder included
	in the archive). Empty subfolders will be included in the archive
	as well.
	"""
	parent_folder = os.path.dirname(folder_path)
	# Retrieve the paths of the folder contents.
	contents = os.walk(folder_path)
	try:
		zip_file = zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED)
		for root, folders, files in contents:
			# Include all subfolders, including empty ones.
			for folder_name in folders:
				absolute_path = os.path.join(root, folder_name)
				relative_path = absolute_path.replace(parent_folder + '\\',
													  '')
				print "Adding '%s' to archive." % absolute_path
				zip_file.write(absolute_path, relative_path)
			for file_name in files:
				absolute_path = os.path.join(root, file_name)
				relative_path = absolute_path.replace(parent_folder + '\\',
													  '')
				print "Adding '%s' to archive." % absolute_path
				zip_file.write(absolute_path, relative_path)
		print "'%s' created successfully." % output_path
	except IOError, message:
		print message
		sys.exit(1)
	except OSError, message:
		print message
		sys.exit(1)
	except zipfile.BadZipfile, message:
		print message
		sys.exit(1)
	finally:
		zip_file.close()
		
#Get the arguments to include in the invest.sdr model run
def GetArgs(*args):
	try:
		args = {
			u'carbon_pool_initial_uri': carbon_pool_initial_variables_table,
			u'carbon_pool_transient_uri': carbon_pool_transient_variables_table,
			u'do_economic_analysis': do_economic_analysis,
			u'do_price_table': use_price_table,
			u'lulc_baseline_map_uri': baseline_raster,
			u'lulc_baseline_year': int(year_of_baseline),
			u'lulc_lookup_uri': lulc_lookup_table,
			u'lulc_transition_maps_list': [transition_lulc_raster],
			u'lulc_transition_matrix_uri': lulc_transition_effect_of_carbon_table,
			u'lulc_transition_years_list': [int(transition_year)],
			u'workspace_dir': workspace_dir,
			u'analysis_year': u''
		}
		#check if run economic analysis is checked
		if do_economic_analysis:
			args[u'discount_rate']= discount_rate
			if use_price_table:
				args[u'price_table_uri'] = price_table
			else:
				args[u'interest_rate'] = interest_rate
				args[u'price'] = price	

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	return args

def ModifyRaster(in_raster, new_name):
	try:
		# Get input Raster properties
		inRaster = Raster(in_raster)
		lowerLeft = arcpy.Point(inRaster.extent.XMin,inRaster.extent.YMin)
		cellSize = inRaster.meanCellWidth

		# Convert Raster to numpy array
		arr = arcpy.RasterToNumPyArray(inRaster, nodata_to_value=0)
		#Convert Array to raster (keep the origin and cellsize the same as the input)
		newRaster = arcpy.NumPyArrayToRaster(arr, lowerLeft, cellSize, value_to_nodata=0)
		newRaster.save(os.path.join(arcpy.env.scratchFolder, "outputs_core", new_name))
		del inRaster, newRaster

	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))

	except Exception as ex:
		arcpy.AddError(ex.args[0])
		
#Projection alignment issues exist between ArcGIS and InVEST output. This function corrects these issues.	
def DefineProj(ref_lyr, out_lyr):

	arcpy.AddMessage("Projecting output layers ...")
	try: 
		#get the coordinate system of the reference lyr
		dsc = arcpy.Describe(ref_lyr)
		coord_sys = dsc.spatialReference
		# run the Define Projection GP tool
		arcpy.DefineProjection_management(out_lyr, coord_sys)
		
	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))

	except Exception as ex:
		arcpy.AddError(ex.args[0])
		

if __name__ == '__main__':
	isLicensed()

	##Read input par
	lulc_lookup_table = arcpy.GetParameterAsText(0)
	lulc_transition_effect_of_carbon_table = arcpy.GetParameterAsText(1)
	carbon_pool_initial_variables_table = arcpy.GetParameterAsText(2)
	carbon_pool_transient_variables_table = arcpy.GetParameterAsText(3)
	baseline_raster = arcpy.GetParameterAsText(4)
	year_of_baseline = arcpy.GetParameterAsText(5)
	transition_lulc_raster = arcpy.GetParameterAsText(6)
	transition_year = arcpy.GetParameterAsText(7)
	do_economic_analysis = arcpy.GetParameter(8)
	use_price_table = arcpy.GetParameter(9)
	price = arcpy.GetParameter(10)
	interest_rate = arcpy.GetParameter(11)
	discount_rate = arcpy.GetParameter(12)
	price_table = arcpy.GetParameterAsText(13)

	#Set optional variables to None if they are not provided by user
	if not price:
		price = None
	if not interest_rate:
		interest_rate = None
	if not discount_rate:
		discount_rate = None
	if not price_table:
		price_table = None
		
	#Run the NatCap module
	arcpy.AddMessage("Running InVEST model ...")

	args = GetArgs(lulc_lookup_table, lulc_transition_effect_of_carbon_table,carbon_pool_initial_variables_table, carbon_pool_transient_variables_table, 
	baseline_raster, year_of_baseline, transition_lulc_raster, transition_year,
	do_economic_analysis, use_price_table, price, interest_rate, discount_rate,
	price_table)

	natcap.invest.coastal_blue_carbon.coastal_blue_carbon.execute(args)

	### Create output raster maps ###
	os.chdir(os.path.join(arcpy.env.scratchFolder, "outputs_core"))
	arcpy.AddMessage("Creating output maps ...")
	for lyr in glob.glob("*.tif"):	
		try:
			if ("carbon_stock_at_" + year_of_baseline) in lyr:
				out_carbon_stock = "carbon_stock_at_" + year_of_baseline + '.tif'
				out_carbon_stock_mod = "carbon_stock_at_" + year_of_baseline + '_mod.tif'
				arcpy.AddMessage("Setting Zero Values to Null...") 	
				ModifyRaster(out_carbon_stock, out_carbon_stock_mod)
				##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
				DefineProj(args[u'lulc_baseline_map_uri'], out_carbon_stock_mod)
				out_carbon_stock_path = os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_stock_mod)
				arcpy.SetParameterAsText(14, out_carbon_stock_path)
				os.remove(os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_stock))
			elif ("carbon_stock_at_" + transition_year) in lyr:
				out_carbon_stock = "carbon_stock_at_" + transition_year + '.tif'
				out_carbon_stock_mod = "carbon_stock_at_" + transition_year + '_mod.tif'
				arcpy.AddMessage("Setting Zero Values to Null...") 	
				ModifyRaster(out_carbon_stock, out_carbon_stock_mod)
				##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
				DefineProj(args[u'lulc_baseline_map_uri'], out_carbon_stock_mod)
				out_carbon_stock_path = os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_stock_mod)
				arcpy.SetParameterAsText(15, out_carbon_stock_path)
				os.remove(os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_stock))
			elif "carbon_accumulation_between_" in lyr:
				out_carbon_acc = "carbon_accumulation_between_" + year_of_baseline + '_and_' + transition_year + '.tif'
				out_carbon_acc_mod = "carbon_accumulation_between_" + year_of_baseline + '_and_' + transition_year + '_mod.tif'
				arcpy.AddMessage("Setting Zero Values to Null...") 	
				ModifyRaster(out_carbon_acc, out_carbon_acc_mod)
				##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
				DefineProj(args[u'lulc_baseline_map_uri'], out_carbon_acc_mod)
				out_carbon_acc_path = os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_acc_mod)				
				arcpy.SetParameterAsText(16, out_carbon_acc_path)
				os.remove(os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_acc))
			elif "carbon_emissions_between_" in lyr:
				out_carbon_emiss = "carbon_emissions_between_" + year_of_baseline + '_and_' + transition_year + '.tif'
				out_carbon_emiss_mod = "carbon_emissions_between_" + year_of_baseline + '_and_' + transition_year + '_mod.tif'
				arcpy.AddMessage("Setting Zero Values to Null...") 	
				ModifyRaster(out_carbon_emiss, out_carbon_emiss_mod)
				##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
				DefineProj(args[u'lulc_baseline_map_uri'], out_carbon_emiss_mod)
				out_carbon_emiss_path = os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_emiss_mod)
				arcpy.SetParameterAsText(17, out_carbon_emiss_path)
				os.remove(os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_emiss))
			elif "net_carbon_sequestration_between_" in lyr:
				out_carbon_seq = "net_carbon_sequestration_between_" + year_of_baseline + '_and_' + transition_year + '.tif'
				out_carbon_seq_mod = "net_carbon_sequestration_between_" + year_of_baseline + '_and_' + transition_year + '_mod.tif'
				arcpy.AddMessage("Setting Zero Values to Null...") 	
				ModifyRaster(out_carbon_seq, out_carbon_seq_mod)
				##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
				DefineProj(args[u'lulc_baseline_map_uri'], out_carbon_seq_mod)
				out_carbon_seq_path = os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_seq_mod)
				arcpy.SetParameterAsText(18, out_carbon_seq_path)
				os.remove(os.path.join(arcpy.env.scratchFolder, "outputs_core", out_carbon_seq))
			elif "net_present_value" in lyr:
				out_net_value = 'net_present_value.tif'
				out_net_value_mod = 'net_present_value_mod.tif'
				arcpy.AddMessage("Setting Zero Values to Null...") 	
				ModifyRaster(out_net_value, out_net_value_mod)
				##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
				DefineProj(args[u'lulc_baseline_map_uri'], out_net_value_mod)
				out_net_value_path = os.path.join(arcpy.env.scratchFolder, "outputs_core", out_net_value_mod)
				arcpy.SetParameterAsText(19, out_net_value_path)
				os.remove(os.path.join(arcpy.env.scratchFolder, "outputs_core", out_net_value))
			else:
				pass
				
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))
		except Exception as ex:
			arcpy.AddError(ex.args[0])

	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all maps output...")
	files = [file for file in os.listdir(os.path.join(arcpy.env.scratchFolder, "outputs_core")) if (os.path.isfile(os.path.join(arcpy.env.scratchFolder, "outputs_core", file)) and not file.endswith((".xml", ".tfw")))]
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	for zip_file in files:
		myzip.write(zip_file, compress_type=zipfile.ZIP_DEFLATED)

	arcpy.SetParameterAsText(20, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))	
	