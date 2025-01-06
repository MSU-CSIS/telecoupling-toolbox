#Import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import shutil
import natcap.invest.seasonal_water_yield.seasonal_water_yield

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder	

#List of output files
_OUTPUT = {
	'aggregated_results': r'aggregated_results.shp',
	'B': r'B.tif',
	'B_sum': r'B_sum.tif',
	'CN': r'CN.tif',
	'L': r'L.tif',
	'L_avail': r'L_avail.tif',
	'L_sum': r'L_sum.tif',
	'L_sum_avail': r'L_sum_avail.tif',
	'QF': r'QF.tif',
	'Vri': r'Vri.tif'
}

#Get the arguments to include in the invest.seasonal_water_yield model run
def GetArgs():
	ET = arcpy.GetParameterAsText(0)
	precip = arcpy.GetParameterAsText(1)
	dem = arcpy.GetParameterAsText(2)
	lulc = arcpy.GetParameterAsText(3)
	soil_group = arcpy.GetParameterAsText(4)
	aoi_watershed = arcpy.GetParameterAsText(5)
	bio_table = arcpy.GetParameterAsText(6)
	rain_table = arcpy.GetParameterAsText(7)
	alpha_m = arcpy.GetParameterAsText(8)
	beta_i = arcpy.GetParameterAsText(9)
	gamma = arcpy.GetParameterAsText(10)
	threshold_flow_acc = arcpy.GetParameterAsText(11)
	
	rastList = []
	
	try:
	
		args = {
			u'et0_dir': ET,
			u'precip_dir': precip,
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
	
def defProj(coord_ref, out_rast1, out_rast2, out_rast3, out_rast4, out_rast5, out_rast6, out_rast7, out_rast8, out_rast9, out_shp):
	
	try:
		#Get the coordinate system of the DEM
		coordSys = arcpy.Describe(coord_ref).spatialReference
		
		#Apply the DEM's spatial reference to the output rasters
		rasterList = [out_rast1, out_rast2, out_rast3, out_rast4, out_rast5, out_rast6, out_rast7, out_rast8, out_rast9]
		for r in rasterList:
			arcpy.DefineProjection_management(r, coordSys)
			
		#Apply the DEM's spatial reference to the output shapefile
		arcpy.DefineProjection_management(out_shp, coordSys)
		
	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))
		
	except Exception as ex:
		arcpy.AddError(ex.args[0])


if __name__ == '__main__':
	args = GetArgs()
	
	#Run the Nat Cap module
	natcap.invest.seasonal_water_yield.seasonal_water_yield.execute(args)
	
	#Assign Nat Cap model output to variables
	agg_results_shp = os.path.join(arcpy.env.scratchFolder, _OUTPUT['aggregated_results'])
	b_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['B'])
	b_sum_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['B_sum'])
	cn_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['CN'])
	l_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['L'])
	l_avail_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['L_avail'])
	l_sum_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['L_sum'])
	l_sum_avail_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['L_sum_avail'])
	qf_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['QF'])
	vri_rast = os.path.join(arcpy.env.scratchFolder, _OUTPUT['Vri'])
	
	#Define the projection of each of the output files
	defProj(args[u'dem_raster_path'], b_rast, b_sum_rast, cn_rast, l_rast, l_avail_rast, l_sum_rast, l_sum_avail_rast, qf_rast, vri_rast, agg_results_shp)
	
	#Remove the intermediate folder
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	
	#Add outputs to map viewer
	arcpy.SetParameter(12, b_rast)
	arcpy.SetParameter(13, b_sum_rast)
	arcpy.SetParameter(14, cn_rast)
	arcpy.SetParameter(15, l_rast)
	arcpy.SetParameter(16, l_avail_rast)
	arcpy.SetParameter(17, l_sum_rast)
	arcpy.SetParameter(18, l_sum_avail_rast)
	arcpy.SetParameter(19, qf_rast)
	arcpy.SetParameter(20, vri_rast)
	arcpy.SetParameter(21, agg_results_shp)
