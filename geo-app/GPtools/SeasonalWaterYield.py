#Import all modules
import arcpy, os, sys, shutil, glob, zipfile
from arcpy.sa import *
import natcap.invest.seasonal_water_yield.seasonal_water_yield

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
			u'et0_dir': ET_dir,
			u'precip_dir': precip_dir,
			u'dem_raster_path': dem,
			u'lulc_raster_path': lulc,
			u'soil_group_path': soil_group,
			u'aoi_path': aoi_watershed,
			u'biophysical_table_path': bio_table,
			u'rain_events_table_path': rain_table,
			u'alpha_m': alpha_m,
			u'beta_i': beta_i,
			u'gamma': gamma,
			u'threshold_flow_accumulation': threshold_flow_acc,
			u'climate_zone_raster_path': u'',
			u'climate_zone_table_path': u'',
			u'l_path': u'',
			u'monthly_alpha': False,
			u'monthly_alpha_path': u'',
			u'user_defined_climate_zones': False,
			u'user_defined_local_recharge': False,
			u'workspace_dir': workspace_dir
		}
		
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
	ET_zip = arcpy.GetParameterAsText(0)
	precip_zip = arcpy.GetParameterAsText(1)
	dem = arcpy.GetParameterAsText(2)
	lulc = arcpy.GetParameterAsText(3)
	soil_group = arcpy.GetParameterAsText(4)
	aoi_watershed_zip = arcpy.GetParameterAsText(5)
	bio_table = arcpy.GetParameterAsText(6)
	rain_table = arcpy.GetParameterAsText(7)
	alpha_m = arcpy.GetParameter(8)
	beta_i = arcpy.GetParameter(9)
	gamma = arcpy.GetParameter(10)
	threshold_flow_acc = arcpy.GetParameter(11)

	#Unzip input folders	
	arcpy.AddMessage("Unzipping Evapotranspiration Folder ...")
	unZipFile(ET_zip, "ET")
	ET_dir = os.path.join(arcpy.env.scratchFolder, "ET") 

	arcpy.AddMessage("Unzipping Precipitation Folder ...")
	unZipFile(precip_zip, "precip")
	precip_dir = os.path.join(arcpy.env.scratchFolder, "precip") 	
	
	#Unzip input aoi
	arcpy.AddMessage("Unzipping AOI Shapefile ...")
	unZipFile(aoi_watershed_zip, "aoi_watershed")
	#the following block is necessary b/c the remote server changes uploaded zip name randomly
	#in order to retrieve the actual shp file name, list files inside unzipped folder
	aoi_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "aoi_watershed"))
	for file in aoi_dir:
		if file.endswith(".shp"):
			aoi_shp_name = file
	aoi_watershed = os.path.join(arcpy.env.scratchFolder, "aoi_watershed", aoi_shp_name)
		
	arcpy.AddMessage("Running InVEST model ...")
	args = GetArgs(ET_dir, precip_dir, dem, lulc, soil_group, aoi_watershed, bio_table,
				   rain_table, alpha_m, beta_i, gamma, threshold_flow_acc)
	#Run the InVEST script with the arguments from GetArgs()
	natcap.invest.seasonal_water_yield.seasonal_water_yield.execute(args)

	#Remove intermediate files created by InVEST script
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "aoi_watershed"))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'ET'))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'precip'))	
	
	### Create output raster maps ###
	os.chdir(arcpy.env.scratchFolder)
	arcpy.AddMessage("Creating output nutrient discharge maps for selected areas ...")
	for lyr in glob.glob("*.tif"):
		try:
			##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
			DefineProj(args[u'dem_raster_path'], lyr)
			if lyr in "B.tif":
				out_B = os.path.join(arcpy.env.scratchFolder, "B.tif")
				arcpy.SetParameterAsText(12, out_B)
			elif lyr == "QF.tif":
				out_QF = os.path.join(arcpy.env.scratchFolder, "QF.tif")
				arcpy.SetParameterAsText(13, out_QF)
			elif lyr == "L.tif":
				out_L = os.path.join(arcpy.env.scratchFolder, "L.tif")
				arcpy.SetParameterAsText(14, out_L)
				
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))
		except Exception as ex:
			arcpy.AddError(ex.args[0])

	#Create output folder to be zipped with all output maps inside it
	#out_dir = os.path.join(arcpy.env.scratchFolder, "Maps")
	#if not os.path.exists(out_dir):
	#	os.makedirs(out_dir)

	#List all files that are NOT of folder type and loop through it to copy each file into output maps folder
	#files = [file for file in os.listdir(arcpy.env.scratchFolder) if os.path.isfile(os.path.join(arcpy.env.scratchFolder, file))]
	#for file in files:
    #	shutil.copy(file, out_dir)
    
	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all maps output...")
	files = [file for file in os.listdir(arcpy.env.scratchFolder) if (os.path.isfile(os.path.join(arcpy.env.scratchFolder, file)) and not file.endswith(".xml"))]
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	for zip_file in files:
		myzip.write(zip_file, compress_type=zipfile.ZIP_DEFLATED)
	
	#output directory from InVEST model
	#out_maps_zip = os.path.join(arcpy.env.scratchFolder, 'output_maps.zip')
	#zip_folder(os.path.join(arcpy.env.scratchFolder, out_dir), out_maps_zip)
	#shutil.rmtree(os.path.join(arcpy.env.scratchFolder, out_dir))		
	#arcpy.SetParameterAsText(15, out_maps_zip)
	arcpy.SetParameterAsText(15, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))