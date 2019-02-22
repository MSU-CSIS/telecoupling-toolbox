#Import all modules
import arcpy
from arcpy.sa import *
import natcap.invest.ndr.ndr
import os, sys, shutil, zipfile, glob

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

def unZipFile(inFile, dir_name):
	#Create a folder in the directory to extract zip to 
	zipFolder = os.path.join(arcpy.env.scratchFolder, dir_name)  
	# Extract the zip contents
	zip2Extract = zipfile.ZipFile(inFile, 'r')	
	zip2Extract.extractall(zipFolder)
	zip2Extract.close() 
	return
	
#Set the arguments for the invest.ndr script
def GetArgs(*args):
		
	try:
		args = {
			u'dem_path': dem,
			u'lulc_path': lulc,
			u'runoff_proxy_path': nutrient_runoff,
			u'watersheds_path': watersheds,
			u'biophysical_table_path': biophysical_table,
			u'threshold_flow_accumulation': threshold_flow_accumulation,
			u'k_param': k_param,
			u'calc_p': True,
			u'calc_n': True,
			u'workspace_dir': workspace_dir
			}
		
		if args[u'calc_p'] == True:
			args[u'subsurface_critical_length_p'] = subsurface_critical_length_p
			args[u'subsurface_eff_p'] = subsurface_eff_p
			
		if args[u'calc_n'] == True:
			args[u'subsurface_critical_length_n'] = subsurface_critical_length_n
			args[u'subsurface_eff_n'] = subsurface_eff_n

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

	return args

	
#Projection alignment issues exist between ArcGIS and InVEST output. This function corrects these issues.	
def DefineProj(ref_lyr, out_lyr):

	try: 
		#get the coordinate system of the raster dem
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
	dem = arcpy.GetParameterAsText(0)
	lulc = arcpy.GetParameterAsText(1)
	nutrient_runoff = arcpy.GetParameterAsText(2)
	watersheds_zip = arcpy.GetParameterAsText(3)
	biophysical_table = arcpy.GetParameterAsText(4)
	threshold_flow_accumulation = arcpy.GetParameterAsText(5)
	k_param = arcpy.GetParameterAsText(6)
	subsurface_critical_length_p = arcpy.GetParameterAsText(7)
	subsurface_critical_length_n = arcpy.GetParameterAsText(8)
	subsurface_eff_p = arcpy.GetParameterAsText(9)
	subsurface_eff_n = arcpy.GetParameterAsText(10)
	
	#Unzip input watershed shapefile
	arcpy.AddMessage("Unzipping Watershed Shapefile ...")
	unZipFile(watersheds_zip, "watershed")
	#the following block is necessary b/c the remote server changes uploaded zip name randomly
	#in order to retrieve the actual shp file name, list files inside unzipped folder
	watersheds_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "watershed"))
	for file in watersheds_dir:
		if file.endswith(".shp"):
			watersheds_shp_name = file
	watersheds = os.path.join(arcpy.env.scratchFolder, "watershed", watersheds_shp_name)

	args = GetArgs(dem, lulc, nutrient_runoff, watersheds, biophysical_table, threshold_flow_accumulation, k_param, subsurface_critical_length_p, subsurface_critical_length_n, subsurface_eff_p, subsurface_eff_n)	
	#Run the InVEST script with the arguments from GetArgs
	arcpy.AddMessage("Running InVEST model ...")
	natcap.invest.ndr.ndr.execute(args)

	### Create output nutrient (P, N) discharge raster maps ###
	os.chdir(arcpy.env.scratchFolder)
	arcpy.AddMessage("Creating output nutrient discharge maps for selected areas ...")
	for lyr in glob.glob("*.tif"):
		try:
			##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
			DefineProj(args[u'dem_path'], lyr)
			if "p_" in lyr:
				out_p = os.path.join(arcpy.env.scratchFolder, "p_export.tif")
				arcpy.SetParameterAsText(11, out_p)
			else:
				out_n = os.path.join(arcpy.env.scratchFolder, "n_export.tif")
				arcpy.SetParameterAsText(12, out_n)
				
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))
		except Exception as ex:
			arcpy.AddError(ex.args[0])

	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all maps output...")
	files = [file for file in os.listdir(arcpy.env.scratchFolder) if (os.path.isfile(os.path.join(arcpy.env.scratchFolder, file)) and not file.endswith(".xml"))]
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	for zip_file in files:
		myzip.write(zip_file, compress_type=zipfile.ZIP_DEFLATED)
		
	#output zipped folder with InVEST model output
	arcpy.SetParameterAsText(13, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))
				
	#Remove intermediate files created by InVEST script
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "watershed"))