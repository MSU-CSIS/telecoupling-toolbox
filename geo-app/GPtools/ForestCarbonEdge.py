import arcpy
from arcpy.sa import *
import natcap.invest.forest_carbon_edge_effect
import os, shutil, zipfile, sys

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def unZipFile(inFile, dir_name):
	#Create a folder in the directory to extract zip to 
	zipFolder = os.path.join(arcpy.env.scratchFolder, dir_name)  
	# Extract the zip contents
	zip2Extract = zipfile.ZipFile(inFile, 'r')	
	zip2Extract.extractall(zipFolder)
	zip2Extract.close() 
	return
	
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

def GetArgs(*args):

	try:   
		if not compute_forest_edge_effects:
			args = {
				u'lulc_uri': lulc_uri,
				u'biophysical_table_uri': biophysical_table_uri,
				u'compute_forest_edge_effects': False,
				u'workspace_dir': workspace_dir,
			}
		#COMPUTE FOREST EDGE EFFECTS
		else:
			args = {
				u'lulc_uri': lulc_uri,
				u'biophysical_table_uri': biophysical_table_uri,
				u'compute_forest_edge_effects': True,
				u'tropical_forest_edge_carbon_model_shape_uri': tropical_forest_edge_carbon_model_shape_uri,
				u'n_nearest_model_points': n_nearest_model_points,
				u'biomass_to_carbon_conversion_factor': biomass_to_carbon_conversion_factor,
				u'workspace_dir': workspace_dir,
			}

		if 'all' in pools_to_calculate:
			args[u'pools_to_calculate'] = u'all'
		else:
			args[u'pools_to_calculate'] = u'above_ground'

			
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
		newRaster.save(os.path.join(arcpy.env.scratchFolder, new_name))
		del inRaster, newRaster

	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))

	except Exception as ex:
		arcpy.AddError(ex.args[0])
		
		
def DefineProj(ref_lyr, out_lyr):

	try:
		# get the coordinate system by describing a feature class
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
	lulc_uri = arcpy.GetParameterAsText(0)
	biophysical_table_uri = arcpy.GetParameterAsText(1)
	pools_to_calculate = arcpy.GetParameterAsText(2)
	compute_forest_edge_effects = arcpy.GetParameter(3)
	tropical_forest_edge_carbon_model_shape_zip = arcpy.GetParameterAsText(4)
	n_nearest_model_points = arcpy.GetParameter(5)
	biomass_to_carbon_conversion_factor = arcpy.GetParameter(6)

	#Unzip input carbon edge shapefile
	if compute_forest_edge_effects and tropical_forest_edge_carbon_model_shape_zip:
		arcpy.AddMessage("Unzipping Edge Shapefile ...")
		dir_name = "edge"
		unZipFile(tropical_forest_edge_carbon_model_shape_zip, dir_name)
		unzip_folder_path = os.path.join(arcpy.env.scratchFolder, dir_name)
		file_lst = os.listdir(unzip_folder_path)
		file_basename = os.path.basename(file_lst[0])
		edge_shp = os.path.splitext(file_basename)[0] + ".shp"
		tropical_forest_edge_carbon_model_shape_uri = os.path.join(arcpy.env.scratchFolder, dir_name, edge_shp)
	else:
		tropical_forest_edge_carbon_model_shape_uri = None				
		
	args = GetArgs(lulc_uri, biophysical_table_uri, pools_to_calculate, compute_forest_edge_effects, 
				   tropical_forest_edge_carbon_model_shape_uri, n_nearest_model_points, biomass_to_carbon_conversion_factor)
	natcap.invest.forest_carbon_edge_effect.execute(args)
	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate_outputs"))
	if tropical_forest_edge_carbon_model_shape_zip:
	    dir_name = "edge"
	    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, dir_name))
		
	outCarbon_rast = os.path.join(arcpy.env.scratchFolder, "carbon_map.tif")
	arcpy.AddMessage("Extracting Yield Mask and Setting Values to Null...") 	
	ModifyRaster(outCarbon_rast, "carbon_map_mod.tif")
	##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
	outCarbon_rast_mod = os.path.join(arcpy.env.scratchFolder, "carbon_map_mod.tif")
	DefineProj(args[u'lulc_uri'], outCarbon_rast_mod)
	#DefineProj(args[u'lulc_uri'], outCarbon_rast)

	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all output...")
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	myzip.write(outCarbon_rast_mod, os.path.basename(outCarbon_rast_mod), compress_type=zipfile.ZIP_DEFLATED)	
	
	#remove file not needed
	os.remove(outCarbon_rast)

	#### Set Parameters ####
	arcpy.SetParameter(7, outCarbon_rast_mod)
	arcpy.SetParameter(8, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))
	#arcpy.SetParameter(7, outCarbon_rast)


    