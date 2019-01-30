# Import all necessary module dependencies
import arcpy, os, sys, shutil, glob, zipfile
import natcap.invest.habitat_risk_assessment.hra

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def GetArgs(*args):

    try:

        args = {
                u'str_uri': stressors_dir,
                u'csv_uri': ratings_dir,
                u'grid_size': grid_size,
                u'risk_eq': risk_eq,
                u'decay_eq': decay_eq,
                u'max_rating': max_rating,
                u'max_stress': max_stress,
                u'aoi_tables': subregions_shp,
                u'workspace_dir': workspace_dir,
                u'spp_uri': layer_dir,
                u'habs_uri': layer_dir
        }

        if criteria_dir:
            args[u'crit_uri'] = criteria_dir

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args

def unZipFile(inFile, dir_name):
    #Create a folder in the directory to extract zip to 
    zipFolder = os.path.join(arcpy.env.scratchFolder, dir_name)  
    # Extract the zip contents
    zip2Extract = zipfile.ZipFile(inFile, 'r')	
    zip2Extract.extractall(zipFolder)
    zip2Extract.close() 
    return

def zip_files(dir_path, out_zip_name, ext):

	os.chdir(dir_path)
	files_grabbed = []
	if ext:
		for files in ext:
			files_grabbed.extend(glob.glob(files))
	try:
		with zipfile.ZipFile(out_zip_name, 'w') as myzip:
			arcpy.AddMessage("Adding desired files to zipped folder...")
			for f in files_grabbed:   
				myzip.write(f)

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
		myzip.close()

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

	##Read input par
	layer_dir_zip = arcpy.GetParameterAsText(0)
	stressors_dir_zip = arcpy.GetParameterAsText(1)
	criteria_dir_zip = arcpy.GetParameterAsText(2)
	ratings_dir_zip = arcpy.GetParameterAsText(3)
	grid_size = arcpy.GetParameter(4)
	risk_eq = arcpy.GetParameterAsText(5)
	decay_eq = arcpy.GetParameterAsText(6)
	max_rating = arcpy.GetParameter(7)
	max_stress = arcpy.GetParameter(8)
	subregions_shp_zip = arcpy.GetParameterAsText(9)

	#Unzip all input zipped files & folders:
	## HABITAT ##
	arcpy.AddMessage("Reading Habitat Shapefile ...")
	unZipFile(layer_dir_zip, "habitat")
	layer_dir = os.path.join(arcpy.env.scratchFolder, "habitat") 
	## STRESSORS ##	
	arcpy.AddMessage("Unzipping Stressor Layers Folder ...")
	unZipFile(stressors_dir_zip, "stressors")
	stressors_dir = os.path.join(arcpy.env.scratchFolder, "stressors") 
	## SPATIAL CRITERIA ##	
	if criteria_dir_zip:
		arcpy.AddMessage("Unzipping Spatial Criteria Layers Folder ...")
		unZipFile(criteria_dir_zip, "sp_criteria")
		criteria_dir = os.path.join(arcpy.env.scratchFolder, "sp_criteria") 
	else:
		criteria_dir = None
	## CRITERIA RATING SCORES ##		
	arcpy.AddMessage("Unzipping Ratings Files Folder ...")
	unZipFile(ratings_dir_zip, "ratings")
	ratings_dir = os.path.join(arcpy.env.scratchFolder, "ratings") 	

	#Unzip subregions shapefile
	arcpy.AddMessage("Unzipping Subregions Shapefile ...")
	unZipFile(subregions_shp_zip, "sub_shp")
	subregions_shp_name = os.path.basename(subregions_shp_zip).strip('.zip') + ".shp"
	subregions_shp = os.path.join(arcpy.env.scratchFolder, "sub_shp", subregions_shp_name)

	#create dictionary of args to pass onto the InVEST model execute function
	arcpy.AddMessage("Parsing input parameters...")
	args = GetArgs(layer_dir, stressors_dir, criteria_dir, ratings_dir, grid_size, risk_eq, decay_eq, max_rating, max_stress, subregions_shp, workspace_dir)

	#Run the InVEST model
	arcpy.AddMessage("Running InVEST model ...")
	natcap.invest.habitat_risk_assessment.hra.execute(args)

	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "habitat"))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "stressors"))
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "ratings"))
	if criteria_dir_zip:
		shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "sp_criteria"))
	
	### Create output maps zipped file ###
	arcpy.AddMessage("Creating output zipped folder with all maps output...")
	#output directory from InVEST model
	maps_dir = os.path.join(arcpy.env.scratchFolder, 'output', 'Maps') 
	#zip_files(maps_dir, out_maps_zip, ['*.shp', '*.shx', '*.dbf', '*.prj'])
	out_maps_zip = os.path.join(arcpy.env.scratchFolder, 'habitat_risk_maps.zip')
	zip_folder(maps_dir, out_maps_zip)

	### Create output reports file ###
	arcpy.AddMessage("Creating output zipped folder with HTML reports...")
	#output directory from InVEST model
	HTML_plots_dir = os.path.join(arcpy.env.scratchFolder, 'output', 'HTML_Plots')
	out_HTML_zip = os.path.join(arcpy.env.scratchFolder, 'html_reports.zip')
	zip_folder(HTML_plots_dir, out_HTML_zip)

	### Create output shapefile classified risk maps ###
	os.chdir(maps_dir)
	arcpy.AddMessage("Creating output risk maps for selected habitat/species...")
	for lyr in glob.glob("*.shp"):
		try:
			##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
			DefineProj(args[u'aoi_tables'], lyr)
			out_shp = os.path.join(maps_dir, lyr) 
		except arcpy.ExecuteError:
			arcpy.AddError(arcpy.GetMessages(2))
		except Exception as ex:
			arcpy.AddError(ex.args[0])

	# Process: Create a feature layer from the joined feature class to send back as output to GP tools
	out_shp_name = "Habitat Risk"
	out_fl = arcpy.MakeFeatureLayer_management(out_shp, out_shp_name)  

	#remove entire folder and all its content
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "sub_shp"))
	
	#output file to be returned to GUI
	#### Set Parameters ####
	arcpy.SetParameter(10, out_fl)
	arcpy.SetParameterAsText(11, out_maps_zip)
	arcpy.SetParameterAsText(12, out_HTML_zip)
