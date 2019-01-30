#Import modules
import arcpy, os, sys, shutil, glob, zipfile, csv
from arcpy.sa import *
import natcap.invest.fisheries.fisheries

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
	
		args = {
				u'aoi_uri': aoi,
				u'total_timesteps': steps,
				u'population_type': population_type,
				u'sexsp': sexsp,
				u'harvest_units': harvest_units,
				u'population_csv_uri': population_csv_uri,
				u'total_init_recruits': total_init_recruits,
				u'recruitment_type': recruit_func,
				u'spawn_units': spawn_units,
				u'alpha': alpha,
				u'beta': beta,
				u'migr_cont': False,
				u'val_cont': False,
				u'do_batch': False,
				u'total_recur_recruits': u'',
				u'workspace_dir': workspace_dir,
				}
		
		if migratory_bool:
			args[u'migr_cont'] = True
			args[u'migration_dir'] = migration_dir
		
		if valuation_bool:
			args[u'val_cont'] = True
			args[u'frac_post_process'] = frac_post_process
			args[u'unit_price'] = unit_price
	
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
	aoi_zip = arcpy.GetParameterAsText(0)
	steps = arcpy.GetParameter(1)
	population_type = arcpy.GetParameterAsText(2)
	sexsp = arcpy.GetParameterAsText(3)
	harvest_units = arcpy.GetParameterAsText(4)
	population_csv_uri = arcpy.GetParameterAsText(5)
	total_init_recruits = arcpy.GetParameter(6)
	recruit_func = arcpy.GetParameterAsText(7)
	spawn_units = arcpy.GetParameterAsText(8)
	alpha = arcpy.GetParameter(9)
	beta = arcpy.GetParameter(10)
	migratory_bool = arcpy.GetParameterAsText(11)
	migration_zip = arcpy.GetParameterAsText(12)
	valuation_bool = arcpy.GetParameterAsText(13)
	frac_post_process = arcpy.GetParameter(14)
	unit_price = arcpy.GetParameter(15)
	
	#Unzip input aoi
	arcpy.AddMessage("Unzipping AOI Shapefile ...")
	unZipFile(aoi_zip, "aoi")
	#the following block is necessary b/c the remote server changes uploaded zip name randomly
	#in order to retrieve the actual shp file name, list files inside unzipped folder
	aoi_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "aoi"))
	for file in aoi_dir:
		if file.endswith(".shp"):
			aoi_shp_name = file
	aoi = os.path.join(arcpy.env.scratchFolder, "aoi", aoi_shp_name)	

	if migration_zip:	
		#Unzip input threat folder file
		arcpy.AddMessage("Unzipping Migrations Folder ...")
		unZipFile(migration_zip, "migrations")
		migration_dir = os.path.join(arcpy.env.scratchFolder, "migrations") 
	else:
		migration_dir = None

	arcpy.AddMessage("Running InVEST model ...")
	args = GetArgs(aoi, steps, population_type, sexsp, harvest_units, population_csv_uri,
			total_init_recruits, recruit_func, spawn_units, alpha, beta, migratory_bool, 
			migration_dir, valuation_bool, frac_post_process, unit_price)
	
	#Run the InVEST script with the arguments from GetArgs()
	natcap.invest.fisheries.fisheries.execute(args)
	
	### Create output shapefile harvest (and value) map ###
	maps_dir = os.path.join(arcpy.env.scratchFolder, 'output')
	os.chdir(maps_dir)
	arcpy.AddMessage("Creating output harvest maps for selected species...")
	for lyr in glob.glob("*.shp"):
		try:
			##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
			DefineProj(args[u'aoi_uri'], lyr)
			out_shp_harv = os.path.join(maps_dir, lyr) 
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))
		except Exception as ex:
			arcpy.AddError(ex.args[0])

	#Output shapefile paths (to match InVEST output)
	out_shp_name = "Total Harvest"
	out_fl_harv = arcpy.MakeFeatureLayer_management(out_shp_harv, out_shp_name)

	#Export feature layer to CSV##
	arcpy.AddMessage('Exporting AOI results layer to CSV Table ...')
	outTable_CSV = os.path.join(arcpy.env.scratchFolder, "Harvest_Value_Table.csv")
	out_shp_harv_basename = os.path.basename(aoi)
	out_shp_harv_name = out_shp_harv_basename[:-4] + "_results_aoi.shp"
	ExportToCSV(fc=os.path.join(arcpy.env.scratchFolder, 'output', out_shp_harv_name), output=outTable_CSV)	
			
	#Output shapefile paths for COPY of InVEST output to create a symbology map service	
	#out_shp_harv_lyrName = out_shp_harv_basename[:-4] + "_tot_harvest.shp"
	#out_shp_harv_copyFC = os.path.join(arcpy.env.scratchFolder, 'output', out_shp_harv_lyrName)
	#inputFC = os.path.join(arcpy.env.scratchFolder, 'output', out_shp_harv_name)
	#arcpy.CopyFeatures_management(inputFC, out_shp_harv_copyFC)
	#out_fl_harv_copyFC = arcpy.MakeFeatureLayer_management(out_shp_harv_copyFC, out_shp_harv_lyrName)
		
	#Output CSV path (to match InVEST output)	
	src = os.path.join(arcpy.env.scratchFolder, "output", "results_table.csv")
	dst = os.path.join(arcpy.env.scratchFolder, "results_table.csv")
	shutil.copyfile(src, dst)
		
	#### Set Parameters ####
	arcpy.SetParameter(16, out_fl_harv)
	arcpy.SetParameter(17, outTable_CSV)
	arcpy.SetParameter(18, dst)

	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all maps output...")
	out_dir = os.path.join(arcpy.env.scratchFolder, "output")
	files = [os.path.join(out_dir, file) for file in os.listdir(out_dir) if not file.endswith((".csv", ".lock"))]
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_files.zip'), 'w')
	# LOOP through the file list and add to the zip file
	for zip_file in files:
		myzip.write(zip_file, os.path.basename(zip_file), compress_type=zipfile.ZIP_DEFLATED)  

	#Set Parameter as InVEST output zip file
	arcpy.SetParameter(19, os.path.join(arcpy.env.scratchFolder, 'output_files.zip'))
	
	#Remove intermediate files created by InVEST script
	if migration_zip:
		shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'migrations'))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate'))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'aoi'))
	#remove file not needed
	os.remove(os.path.join(arcpy.env.scratchFolder, "output", "results_page.html"))