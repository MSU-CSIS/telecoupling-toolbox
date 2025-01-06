#Import modules
import arcpy
from arcpy.sa import *
import natcap.invest.fisheries.fisheries
import os
import sys
import shutil
import ntpath

arcpy.env.overwriteOutput = True
#workspace_dir = arcpy.env.scratchFolder

def GetArgs():
	aoi = arcpy.GetParameterAsText(0)
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
	migratory_yorn = arcpy.GetParameterAsText(11)
	migration_dir = arcpy.GetParameterAsText(12)
	valuation_yorn = arcpy.GetParameterAsText(13)
	frac_post_process = arcpy.GetParameter(14)
	unit_price = arcpy.GetParameter(15)
	outputWorkspace = arcpy.GetParameterAsText(16)
	
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
				u'population_csv_dir': u'',
				u'results_suffix': u'',
				u'workspace_dir': outputWorkspace,
				u'total_recur_recruits': u''
				}
		
		if migratory_yorn == "true":
			args[u'migr_cont'] = True
			args[u'migration_dir'] = migration_dir
		
		if valuation_yorn == "true":
			args[u'val_cont'] = True
			args[u'frac_post_process'] = frac_post_process
			args[u'unit_price'] = unit_price
	
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
	
	return args, aoi, outputWorkspace
	
#Projection alignment issues exist between ArcGIS and InVEST output. This function corrects these issues.
def DefineProj(shp_ref, shp_out):
	
	try:
	
		#Get the coordinate system of the reference shapefile.
		
		dsc = arcpy.Describe(shp_ref)
		coord_sys = dsc.spatialReference
		
		#Apply this coordinate system to the output shapefile.
		arcpy.DefineProjection_management(shp_out, coord_sys)
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))

if __name__ == '__main__':
	args, aoi, outputWorkspace = GetArgs()
	
	#Run the InVEST script with the arguments from GetArgs()
	natcap.invest.fisheries.fisheries.execute(args)
	
	#Output files
	shpName1 = ntpath.basename(aoi)
	shpName2 = shpName1[:-4] + "_results_aoi_.shp"
	
	#Obtain the output shapefile
	outAOI = os.path.join(outputWorkspace, "output", shpName2)
	#outCSV = os.path.join(arcpy.env.scratchFolder, "output", "results_table_.csv")
	
	#Run the DefineProj function to correct projection alignment issues.
	DefineProj(aoi, outAOI)
	
	#Remove intermediate files created by InVEST script
	shutil.rmtree(os.path.join(outputWorkspace, 'intermediate'))
	
	#Add outputs to map viewer
	arcpy.SetParameter(17, outAOI)