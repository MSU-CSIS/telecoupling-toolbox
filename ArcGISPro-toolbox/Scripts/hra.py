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
        }

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    return args

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
    layer_dir = arcpy.GetParameterAsText(0)
    stressors_dir = arcpy.GetParameterAsText(1)
    criteria_dir = arcpy.GetParameterAsText(2)
    ratings_dir = arcpy.GetParameterAsText(3)
    grid_size = arcpy.GetParameter(4)
    risk_eq = arcpy.GetParameterAsText(5)
    decay_eq = arcpy.GetParameterAsText(6)
    max_rating = arcpy.GetParameter(7)
    max_stress = arcpy.GetParameter(8)
    subregions_shp = arcpy.GetParameterAsText(9)

    #create dictionary of args to pass onto the InVEST model execute function
    arcpy.AddMessage("Parsing input parameters...")
    args = GetArgs(layer_dir, stressors_dir, criteria_dir, ratings_dir, grid_size, risk_eq, decay_eq, max_rating, max_stress, subregions_shp, workspace_dir)

    #Run the InVEST model
    arcpy.AddMessage("Running hra model...")
    natcap.invest.habitat_risk_assessment.hra.execute(args)

    ### Create output rasters ###
    '''arcpy.AddMessage("Creating output risk maps...")
    out_lst_rast = []
    # --Output--
    #/output/maps/recov_potent_H[habitatname].tif- Raster layer
    #    depicting the recovery potential of each individual habitat.
    #/output/maps/cum_risk_H[habitatname]- Raster layer depicting the
    #    cumulative risk for all stressors in a cell for the given
    #    habitat.
    #/output/maps/ecosys_risk- Raster layer that depicts the sum of all
    #    cumulative risk scores of all habitats for that cell.
    #/output/maps/[habitatname]_HIGH_RISK- A raster-shaped shapefile
    #    containing only the "high risk" areas of each habitat, defined
    #    as being above a certain risk threshold.
    maps_dir = os.path.join(arcpy.env.scratchFolder, 'output', 'Maps')
    os.chdir(maps_dir)
    for lyr in glob.glob("*.tif"):
        try:
            ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
            #DefineProj(args[u'landuse_cur_uri'], lyr)
            out_rast = os.path.join(maps_dir, lyr)
            out_lst_rast.append(out_rast)

        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as ex:
            arcpy.AddError(ex.args[0])

    ### Set Parameters for raster maps ###
    out_rast_maps = ";".join(out_lst_rast)
    #### Set Parameters ####
    arcpy.SetParameter(10, out_rast_maps)'''

    ### Create output shapefile classified risk maps ###
    maps_dir = os.path.join(arcpy.env.scratchFolder, 'output', 'Maps')
    os.chdir(maps_dir)
    arcpy.AddMessage("Creating output risk maps for each habitat...")
    out_lst_shp = []
    for lyr in glob.glob("*.shp"):
        try:
            ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
            #DefineProj(args[u'landuse_cur_uri'], lyr)
            out_shp = os.path.join(maps_dir, lyr)
            out_lst_shp.append(out_shp)

        except arcpy.ExecuteError:
            arcpy.AddError(arcpy.GetMessages(2))
        except Exception as ex:
            arcpy.AddError(ex.args[0])

    ### Set Parameters for raster maps ###
    out_shp_maps = ";".join(out_lst_shp)
    arcpy.AddMessage(out_shp_maps)
    #### Set Parameters ####
    arcpy.SetParameter(10, out_shp_maps)

    ### Create output reports file ###
    arcpy.AddMessage("Creating output zipped folder with HTML reports...")
    #output directory from InVEST model
    HTML_plots_dir = os.path.join(arcpy.env.scratchFolder, 'output', 'HTML_Plots')
    out_HTML_zip = os.path.join(arcpy.env.scratchFolder, 'html_reports.zip')
    zip_folder(HTML_plots_dir, out_HTML_zip)
    #output file to be returned to GUI
    arcpy.SetParameterAsText(11, out_HTML_zip)

    #remove entire folder and all its content
    shutil.rmtree(os.path.join(arcpy.env.scratchFolder, "intermediate"))
