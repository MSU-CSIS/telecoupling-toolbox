#Import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import shutil
import natcap.invest.coastal_blue_carbon.coastal_blue_carbon

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

#List of output files

_OUTPUT = {
    'rkls': r'rkls.tif',
    'sed_export': r'sed_export.tif',
    'sed_retention_index': r'sed_retention_index.tif',
	'stream': r'stream.tif',
	'usle': r'usle.tif',
	'water_result_sdr': r'water_result_sdr.shp',
	'sed_retention': r'sed_retention.tif'
}

#Get the arguments to include in the invest.sdr model run
def GetArgs():
	biophysical_table = arcpy.GetParameterAsText(0)
	dem = arcpy.GetParameterAsText(1)
	erodibility = arcpy.GetParameterAsText(2)
	erosivity = arcpy.GetParameterAsText(3)
	IC_param = arcpy.GetParameterAsText(4)
	K_param = arcpy.GetParameterAsText(5)
	lulc = arcpy.GetParameterAsText(6)
	sdr_max = arcpy.GetParameterAsText(7)
	threshold_flow_acc = arcpy.GetParameterAsText(8)
	watersheds = arcpy.GetParameterAsText(9)
	#new
	drainage_path = arcpy.GetParameterAsText(10)
	#new
	#drainage_file = arcpy.GetParameterAsText(11)
	
	outRast = []
	
	try:
	
		args = {
			u'biophysical_table_path': biophysical_table,
			u'dem_path': dem,
			#edited
			#u'drainage_path': u''
			#u'drainage_path': False,
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
		
		#new
		if drainage_path:
			args[u'drainage_path'] = drainage_path
			#args[u'drainage_file'] = drainage_file
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	return args
	
if __name__ == '__main__':
	args = GetArgs()
	
	#Run the Nat Cap module
	natcap.invest.sdr.execute(args)
	
	#Assign Nat Cap model output to variables
	rkls = os.path.join(arcpy.env.scratchFolder, _OUTPUT['rkls'])
	sed_export = os.path.join(arcpy.env.scratchFolder, _OUTPUT['sed_export'])
	sed_retention_index = os.path.join(arcpy.env.scratchFolder, _OUTPUT['sed_retention_index'])
	stream = os.path.join(arcpy.env.scratchFolder, _OUTPUT['stream'])
	usle = os.path.join(arcpy.env.scratchFolder, _OUTPUT['usle'])
	water_result_sdr = os.path.join(arcpy.env.scratchFolder, _OUTPUT['water_result_sdr'])
	sed_retention = os.path.join(arcpy.env.scratchFolder, _OUTPUT['sed_retention'])
	
	#Define the projection of each of the output files
	#defProj(args[u'dem_raster_path'], b_rast, b_sum_rast, cn_rast, l_rast, l_avail_rast, l_sum_rast, l_sum_avail_rast, qf_rast, vri_rast, agg_results_shp)
	
	#Remove the intermediate folder
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	
	#Add outputs to map viewer
	arcpy.SetParameter(11, rkls)
	arcpy.SetParameter(12, sed_export)
	arcpy.SetParameter(13, sed_retention_index)
	arcpy.SetParameter(14, stream)
	arcpy.SetParameter(15, usle)
	arcpy.SetParameter(16, water_result_sdr)
	arcpy.SetParameter(17, sed_retention)
