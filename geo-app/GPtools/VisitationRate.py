import arcpy, os, sys, zipfile, shutil
import natcap.invest.recreation.recmodel_client

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

def CleanFields(input_lyr, str):

	try:
		### Create list of fields from input layer ###
		FieldsObj = arcpy.ListFields(input_lyr)
		discard = []  
		for field in [f.name for f in FieldsObj if f.type not in ("OID", "Geometry")]:  
			if str not in field:  
				discard.append(field) 

		### Delete discarded fields from input layer ####
		arcpy.DeleteField_management(input_lyr, discard)
		
	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))

	except Exception as ex:
		arcpy.AddError(ex.args[0])		
		
	return 
	
def GetArgs(*args):

    try:
        args = {
            u'start_year': start_year,
            u'end_year': end_year,
            u'grid_aoi': grid_aoi,
            u'workspace_dir': workspace_dir,
        }
        if aoi_path:
            args[u'aoi_path'] = aoi_path

        if grid_aoi and grid_type != 'none':
            args[u'grid_type'] = grid_type
            args[u'cell_size'] = cell_size

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args

	
if __name__ == '__main__':

	##Read input par
	aoi_path_zip = arcpy.GetParameterAsText(0)
	start_year = arcpy.GetParameterAsText(1)
	end_year = arcpy.GetParameterAsText(2)
	grid_aoi = arcpy.GetParameter(3)
	grid_type = arcpy.GetParameterAsText(4)
	cell_size = arcpy.GetParameter(5)

	if aoi_path_zip:
		##Unzip input AOI shapefile
		arcpy.AddMessage("Unzipping Shapefile ...")
		unZipFile(aoi_path_zip, "AOI")	
		#the following block is necessary b/c the remote server changes uploaded zip name randomly
		#in order to retrieve the actual shp file name, list files inside unzipped folder
		aoi_dir = os.listdir(os.path.join(arcpy.env.scratchFolder, "AOI"))
		for file in aoi_dir:
			if file.endswith(".shp"):
				aoi_shp_name = file
		aoi_path = os.path.join(arcpy.env.scratchFolder, "AOI", aoi_shp_name)
	else:
		aoi_path = None	

	arcpy.AddMessage("Running InVEST model ...")
	args = GetArgs(aoi_path, start_year, end_year, grid_aoi, grid_type, cell_size)
	
	#Run the InVEST script with the arguments from GetArgs()
	natcap.invest.recreation.recmodel_client.execute(args)
		
	#### Connect to Output Files ####
	out_pud_shp = os.path.join(arcpy.env.scratchFolder, 'pud_results.shp')
	out_monthlyTab_csv = os.path.join(arcpy.env.scratchFolder, 'monthly_table.csv')

	##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
	DefineProj(args[u'aoi_path'], out_pud_shp)

	### This step remove unwanted fields from the input layer based on a specified string
	CleanFields(out_pud_shp, "PUD_")
	
	#remove entire folder and all its content
	if aoi_path_zip:
		shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "AOI"))

	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all output...")
	files = [os.path.join(arcpy.env.scratchFolder, file) for file in os.listdir(arcpy.env.scratchFolder) if (os.path.isfile(os.path.join(arcpy.env.scratchFolder, file)) and not file.endswith((".csv", ".xml")))]
	#create zipfile object as speficify 'w' for 'write' mode
	myzip = zipfile.ZipFile(os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'), 'w')
	# LOOP through the file list and add to the zip file
	for zip_file in files:
		myzip.write(zip_file, os.path.basename(zip_file), compress_type=zipfile.ZIP_DEFLATED)
	
	#### Set Parameters ####
	arcpy.SetParameterAsText(6, out_pud_shp)
	arcpy.SetParameterAsText(7, out_monthlyTab_csv)
	arcpy.SetParameterAsText(8, os.path.join(arcpy.env.scratchFolder, 'output_maps.zip'))

