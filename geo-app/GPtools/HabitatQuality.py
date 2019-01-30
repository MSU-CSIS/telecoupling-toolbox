import natcap.invest.habitat_quality
import arcpy
from arcpy.sa import *
import os, glob, shutil, sys, zipfile

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
		
def GetArgs(*args):

	try:
		if landuse_cur_uri:
			args = {
					u'half_saturation_constant': half_saturation_constant,
					u'landuse_cur_uri': landuse_cur_uri,
					u'sensitivity_uri': sensitivity_uri,
					u'threat_raster_folder': threat_raster_folder,
					u'threats_uri': threats_uri,
					u'workspace_dir': workspace_dir,
			}
			if access_uri:
					args[u'access_uri'] = access_uri

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

	return args

def ClampRaster(in_raster, new_name):
	try:
		inRaster = Raster(in_raster)
		outCon = Con(inRaster >= 0, inRaster, 0)
		#outFile = os.path.splitext(in_raster)[0] + "_cl0.tif"
		outCon.save(os.path.join(arcpy.env.scratchFolder, "output", new_name))
		del inRaster, outCon
		os.remove(in_raster)

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
	landuse_cur_uri = arcpy.GetParameterAsText(0)
	threat_raster_zip = arcpy.GetParameterAsText(1)
	threats_uri = arcpy.GetParameterAsText(2)
	access_uri_zip = arcpy.GetParameterAsText(3)
	sensitivity_uri = arcpy.GetParameterAsText(4)
	half_saturation_constant = arcpy.GetParameter(5)

	#Unzip input threat folder file
	arcpy.AddMessage("Unzipping Threats Folder ...")
	unZipFile(threat_raster_zip, "threats")
	threat_raster_folder = os.path.join(arcpy.env.scratchFolder, "threats") 

	#Unzip input access shapefile
	if access_uri_zip:
		arcpy.AddMessage("Unzipping Access Shapefile ...")
		unZipFile(access_uri_zip, "access")
		access_shp_name = os.path.basename(access_uri_zip).strip('.zip') + ".shp"
		access_uri = os.path.join(arcpy.env.scratchFolder, "access", access_shp_name)
	else:
		access_uri = None	
		
	arcpy.AddMessage("Running InVEST model ...")			
	args = GetArgs(landuse_cur_uri, access_uri, threat_raster_folder, threats_uri, sensitivity_uri, half_saturation_constant)	
	natcap.invest.habitat_quality.execute(args)

	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "threats"))
	#remove entire folder and all its content
	if access_uri_zip:
		shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "access"))
		
	os.chdir(os.path.join(arcpy.env.scratchFolder, "output"))
	for lyr in glob.glob("*.tif"):
		try:	
			##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
			DefineProj(args[u'landuse_cur_uri'], lyr)
			if "deg_sum_out_c" in lyr:
				arcpy.AddMessage("Clampling Habitat Degradation Output ...")
				ClampRaster(lyr, "deg_c.tif")
				out_rast = os.path.join(arcpy.env.scratchFolder, "output", "deg_c.tif")
				arcpy.SetParameterAsText(6, out_rast)
			else:
				arcpy.AddMessage("Clampling Habitat Quality Output ...")
				ClampRaster(lyr, "quality_c.tif")
				out_rast = os.path.join(arcpy.env.scratchFolder, "output", "quality_c.tif")
				arcpy.SetParameterAsText(7, out_rast)
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))	
		except Exception as ex:
			arcpy.AddError(ex.args[0])		
    
	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all maps output...")
	out_dir = os.path.join(arcpy.env.scratchFolder, "output")
	files = [os.path.join(out_dir, file) for file in os.listdir(out_dir) if file.endswith(".tif")]
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	for zip_file in files:
		myzip.write(zip_file, os.path.basename(zip_file), compress_type=zipfile.ZIP_DEFLATED)   

	#Set Parameter as InVEST output zip file
	arcpy.SetParameter(8, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))