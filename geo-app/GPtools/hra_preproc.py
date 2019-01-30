# Import all necessary module dependencies
import arcpy, os, sys, shutil, zipfile
import natcap.invest.habitat_risk_assessment.hra_preprocessor

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

def GetArgs(*args):

    try:
        if len(exposure_str) == 0 or len(sensitivity_str) == 0 or len(resilience_str) == 0:
            arcpy.AddError("Choose at least 1 criteria for each category!")
            raise arcpy.ExecuteError

        if (len(exposure_str) + len(sensitivity_str) + len(resilience_str)) < 4:
            arcpy.AddError("Choose at least 4 criteria total between all categories!")
            raise arcpy.ExecuteError

        args = {
                u'stressors_dir': stressors_dir,
                u'exposure_crits': exposure_str,
                u'sensitivity_crits': sensitivity_str,
                u'resilience_crits': resilience_str,
                u'workspace_dir': workspace_dir,
                u'habitats_dir': layer_dir,
                u'species_dir': layer_dir,
        }

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    except arcpy.ExecuteError:
        arcpy.AddError("Choose at least 1 criteria for each category!")

    return args

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
		
		
if __name__ == '__main__':

    ##Read input par
    layer_dir_zip = arcpy.GetParameterAsText(0)
    stressors_dir_zip = arcpy.GetParameterAsText(1)
    exposure_str = arcpy.GetParameterAsText(2)
    sensitivity_str = arcpy.GetParameterAsText(3)
    resilience_str = arcpy.GetParameterAsText(4)
    do_criteria_bool = arcpy.GetParameter(5)
    criteria_dir_zip = arcpy.GetParameterAsText(6)

    exposure_str = exposure_str.split(',')
    exposure_str = [str.strip() for str in exposure_str]

    sensitivity_str = sensitivity_str.split(',')
    sensitivity_str = [str.strip() for str in sensitivity_str]
	
    resilience_str = resilience_str.split(',')
    resilience_str = [str.strip() for str in resilience_str]
	
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
	
    #create dictionary of args to pass onto the InVEST model execute function
    arcpy.AddMessage("Parsing input parameters...")
    args = GetArgs(layer_dir, stressors_dir, exposure_str, sensitivity_str, resilience_str, do_criteria_bool, criteria_dir, workspace_dir)

    #Run the InVEST model
	arcpy.AddMessage("Running InVEST model ...")
    natcap.invest.habitat_risk_assessment.hra_preprocessor.execute(args)

	#remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "habitat"))
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "stressors"))
    if criteria_dir_zip:
        shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "sp_criteria"))

    #zip ratings folder to send back as derived output
    arcpy.AddMessage("Creating output zipped folder with criteria scores...")	
    #output directory from InVEST model	
    out_ratings_folder = os.path.join(arcpy.env.scratchFolder, "habitat_stressor_ratings")
    out_ratings_zip = os.path.join(arcpy.env.scratchFolder, 'criteria_scores.zip')
    zip_folder(out_ratings_folder, out_ratings_zip)	
    #output file to be returned to GUI
    arcpy.SetParameterAsText(7, out_ratings_zip)
	
	#remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "habitat_stressor_ratings"))
