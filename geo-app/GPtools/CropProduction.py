import arcpy
from arcpy.sa import *
import natcap.invest.crop_production.crop_production
import os, sys, zipfile, shutil, numpy

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

		args = {
			u'lookup_table': lookup_table,
			u'aoi_raster': aoi_raster,
			u'dataset_dir': dataset_dir,
			u'yield_function': yield_function,
			u'compute_financial_analysis': False,
			u'compute_nutritional_contents': False,
			u'workspace_dir': workspace_dir,
			u'results_suffix': u'',
		}

		if fertilizer_dir:
			args[u'fertilizer_dir'] = fertilizer_dir

		if yield_function == 'percentile' and percentile_column != 'none':
			args[u'percentile_column'] = percentile_column
		if yield_function == 'regression':
			if not fertilizer_dir:
				arcpy.AddError("A fertilizer raster folder is required when choosing regression as 'Yield Function'!")
				raise SystemExit()
			args[u'irrigation_raster'] = irrigation_raster

		if compute_financial_analysis:
			args[u'compute_financial_analysis'] = True
			args[u'economics_table'] = economics_table

		if compute_nutritional_contents:
			args[u'compute_nutritional_contents'] = True
			args[u'nutrient_table'] = nutrient_table

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
		newRaster.save(os.path.join(arcpy.env.scratchFolder, "output", new_name))
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
	lookup_table = arcpy.GetParameterAsText(0)
	aoi_raster = arcpy.GetParameterAsText(1)
	#dataset_dir_zip = arcpy.GetParameterAsText(2)
	yield_function = arcpy.GetParameterAsText(2)
	percentile_column = arcpy.GetParameterAsText(3)
	fertilizer_dir_zip = arcpy.GetParameterAsText(4)
	irrigation_raster = arcpy.GetParameterAsText(5)
	compute_nutritional_contents = arcpy.GetParameter(6)
	nutrient_table = arcpy.GetParameterAsText(7)
	compute_financial_analysis = arcpy.GetParameter(8)
	economics_table = arcpy.GetParameterAsText(9)

	#Unzip input global dataset folder file
	#arcpy.AddMessage("Unzipping Global Dataset Folder ...")
	#unZipFile(dataset_dir_zip, "global_dataset")
	#dataset_dir = os.path.join(arcpy.env.scratchFolder, "global_dataset") 
	dataset_dir = r"D:\data\telecoupling-geoapp\GPtools\6SocioEconomic Analysis\ToolData\crop\global_dataset"

	if not irrigation_raster:
		irrigation_raster = None

	if percentile_column == 'none':
		percentile_column = None		

	if fertilizer_dir_zip:
		arcpy.AddMessage("Unzipping Fertilizer Dataset Folder ...")
		unZipFile(fertilizer_dir_zip, "fertilizer")
		fertilizer_dir = os.path.join(arcpy.env.scratchFolder, "fertilizer") 	
	else:
		fertilizer_dir = None

	if not economics_table:
		economics_table = None

	if not nutrient_table:
		nutrient_table = None

		
	args = GetArgs(lookup_table, aoi_raster, dataset_dir, yield_function, percentile_column, fertilizer_dir, irrigation_raster,
				   compute_nutritional_contents, nutrient_table, compute_financial_analysis, economics_table)
				   
	arcpy.AddMessage("Running InVEST model ...")				   
	natcap.invest.crop_production.crop_production.execute(args)

	#remove entire folder and all its content
	#shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "global_dataset"))
	if fertilizer_dir_zip:
		#remove entire folder and all its content
		shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "fertilizer"))

	out_yield = os.path.join(arcpy.env.scratchFolder, "output", "yield.tif")

	##This step is a workaround the fact that yield output from InVEST is not masked to the
	##input raster area but rather a rectangular frame encompassing the entire extent
	#### Mask and Set Null values for yield equal to zero ####
	arcpy.AddMessage("Extracting Yield Mask and Setting Values to Null...") 	
	ModifyRaster(out_yield, "yield_mod.tif")
	out_yield_mod = os.path.join(arcpy.env.scratchFolder, "output", "yield_mod.tif")	
	##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
	DefineProj(args[u'aoi_raster'], out_yield_mod)
		
	#remove file not needed
	os.remove(os.path.join(arcpy.env.scratchFolder, "output", "yield.tif"))
	
	#### Set Parameters ####
	arcpy.SetParameter(10, out_yield_mod)
	if args[u'compute_financial_analysis'] == True:
		src = os.path.join(arcpy.env.scratchFolder, "output", "financial_analysis.csv")
		dst = os.path.join(arcpy.env.scratchFolder, "financial_analysis.csv")
		shutil.copyfile(src, dst)
		arcpy.SetParameter(11, dst)
	if args[u'compute_nutritional_contents'] == True:
		src = os.path.join(arcpy.env.scratchFolder, "output", "nutritional_analysis.csv")
		dst = os.path.join(arcpy.env.scratchFolder, "nutritional_analysis.csv")
		shutil.copyfile(src, dst)
		arcpy.SetParameter(12, dst)
		
	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all output...")
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	myzip.write(out_yield_mod, os.path.basename(out_yield_mod), compress_type=zipfile.ZIP_DEFLATED)		

	#Set Parameter as InVEST output zip file
	arcpy.SetParameter(13, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))