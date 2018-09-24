#Import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import shutil
import natcap.invest.sdr

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

#List of output files

_OUTPUT = {
    'rkls': r'rkls.tif',
    'sed_export': r'sed_export.tif',
    'sed_retention_index': r'sed_retention_index.tif',
	'stream': r'stream.tif',
	'usle': r'usle.tif',
	'water_result_sdr': r'watershed_results_sdr.shp',
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
	drainage_path = arcpy.GetParameterAsText(10)
	
	outRast = []
	
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
		
		if drainage_path:
			args[u'drainage_path'] = drainage_path
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	return args

#Projection alignment issues exist between ArcGIS and InVEST output. This function corrects these issues.	
def DefineProj(raster_ref, rast_out, shp_ref, shp_out):

	try: 
	
		#get the coordinate system of the raster dem
		dsc = arcpy.Describe(raster_ref)
		coord_sys = dsc.spatialReference
		
		for i in rast_out:
			arcpy.DefineProjection_management(i, coord_sys)

		#get the coordinate system of the shapefile watershed_results_ndr
		dsc = arcpy.Describe(shp_ref)
		coord_sys = dsc.spatialReference
		
		#apply this coordinate system to the output watershed shp
		arcpy.DefineProjection_management(shp_out, coord_sys)
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
			
if __name__ == '__main__':
	args = GetArgs()
	
	#Run the Nat Cap module
	natcap.invest.sdr.execute(args)
	
	#Output files from InVEST script
	rkls = os.path.join(arcpy.env.scratchFolder, _OUTPUT['rkls'])
	sed_export = os.path.join(arcpy.env.scratchFolder, _OUTPUT['sed_export'])
	sed_retention_index = os.path.join(arcpy.env.scratchFolder, _OUTPUT['sed_retention_index'])
	stream = os.path.join(arcpy.env.scratchFolder, _OUTPUT['stream'])
	usle = os.path.join(arcpy.env.scratchFolder, _OUTPUT['usle'])
	water_result_sdr = os.path.join(arcpy.env.scratchFolder, _OUTPUT['water_result_sdr'])
	sed_retention = os.path.join(arcpy.env.scratchFolder, _OUTPUT['sed_retention'])
	
	out_rast_list = [rkls, sed_export, sed_retention_index, 
					stream, usle, water_result_sdr, sed_retention]

	#Define the projection of each of the output files
	DefineProj(args['dem_path'], out_rast_list, args['watersheds_path'], water_result_sdr)
	
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
