#Import all modules
import arcpy, os, sys, shutil, glob, zipfile, itertools
from arcpy.sa import *
import natcap.invest.sdr

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
		
#Get the arguments to include in the invest.seasonal_water_yield model run
def GetArgs(*args):
	try:
		args = {
			u'biophysical_table_path': biophysical_table,
			u'dem_path': dem,
			u'erodibility_path': erodibility,
			u'erosivity_path': erosivity,
			u'ic_0_param': IC_param,
			u'k_param': K_param,
			u'lulc_path': lulc,
			u'sdr_max': sdr_max,
			u'threshold_flow_accumulation': threshold_flow_acc,
			u'watersheds_path': watersheds,
			u'workspace_dir': workspace_dir
		}
		#check if drainage file is provided
		if drainage_path:
			args[u'drainage_path'] = drainage_path
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

	return args
	
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
	biophysical_table = arcpy.GetParameterAsText(0)
	dem = arcpy.GetParameterAsText(1)
	erodibility = arcpy.GetParameterAsText(2)
	erosivity = arcpy.GetParameterAsText(3)
	IC_param = arcpy.GetParameter(4)
	K_param = arcpy.GetParameter(5)
	lulc = arcpy.GetParameterAsText(6)
	sdr_max = arcpy.GetParameter(7)
	threshold_flow_acc = arcpy.GetParameter(8)
	watersheds_zip = arcpy.GetParameterAsText(9)
	drainage_path = arcpy.GetParameterAsText(10)	
	
	if not drainage_path:
		drainage_path = None
	
	#Unzip input aoi
	arcpy.AddMessage("Unzipping AOI Shapefile ...")
	unZipFile(watersheds_zip, "watersheds")
	#the following block is necessary b/c the remote server changes uploaded zip name randomly
	#in order to retrieve the actual shp file name, list files inside unzipped folder
	aoi_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "watersheds"))
	for file in aoi_dir:
		if file.endswith(".shp"):
			aoi_shp_name = file
	watersheds = os.path.join(arcpy.env.scratchFolder, "watersheds", aoi_shp_name)
	
	#Run the Nat Cap module
	arcpy.AddMessage("Running InVEST model ...")
	args = GetArgs(biophysical_table, dem, erodibility, erosivity, IC_param, K_param, lulc,
				   sdr_max, threshold_flow_acc, watersheds, drainage_path)
	natcap.invest.sdr.execute(args)

	#Remove intermediate files created by InVEST script
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'watersheds'))
	
	### Create output raster maps ###
	os.chdir(arcpy.env.scratchFolder)
	arcpy.AddMessage("Creating output maps for selected areas ...")
	files_grabbed = [glob.glob(e) for e in ["*.tif", "*.shp"]]
	files_grabbed = list(itertools.chain(*files_grabbed))	
	for lyr in files_grabbed:
		try:
			##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
			DefineProj(args[u'dem_path'], lyr)
			if lyr == "watershed_results_sdr.shp":
				out_watersheds_shp = os.path.join(arcpy.env.scratchFolder, "watershed_results_sdr.shp")
				arcpy.SetParameterAsText(11, out_watersheds_shp)
			if lyr == "sed_export.tif":
				out_sed_export = os.path.join(arcpy.env.scratchFolder, "sed_export.tif")
				arcpy.SetParameterAsText(12, out_sed_export)
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

	arcpy.SetParameterAsText(13, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))