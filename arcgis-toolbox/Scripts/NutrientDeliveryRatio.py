#Import all modules
import arcpy
from arcpy.sa import *
import natcap.invest.ndr.ndr
import os
import sys
import shutil

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

#List of output files
_OUTPUT = {
    'watershed_results_shp': r'watershed_results_ndr.shp',
    'p_export': r'p_export.tif',
    'n_export': r'n_export.tif',
}

#Set the arguments for the invest.ndr script
def GetArgs():
	arcpy.AddMessage("in GetArgs.")
	dem = arcpy.GetParameterAsText(0)
	lulc = arcpy.GetParameterAsText(1)
	nutrient_runoff = arcpy.GetParameterAsText(2)
	watersheds = arcpy.GetParameterAsText(3)
	biophysical_table = arcpy.GetParameterAsText(4)
	threshold_flow_accumulation = arcpy.GetParameterAsText(5)
	k_param = arcpy.GetParameterAsText(6)
	subsurfaceFlow = arcpy.GetParameterAsText(7)
	subsurface_critical_length_p = arcpy.GetParameterAsText(8)
	subsurface_critical_length_n = arcpy.GetParameterAsText(9)
	subsurface_eff_p = arcpy.GetParameterAsText(10)
	subsurface_eff_n = arcpy.GetParameterAsText(11)
	
	outRast = []
	
	try:
		
		args = {
			u'dem_path': dem,
			u'lulc_path': lulc,
			u'runoff_proxy_path': nutrient_runoff,
			u'watersheds_path': watersheds,
			u'biophysical_table_path': biophysical_table,
			u'threshold_flow_accumulation': threshold_flow_accumulation,
			u'k_param': k_param,
			u'calc_p': True,
			u'calc_n': True,
			u'workspace_dir': workspace_dir
			}
		
		if subsurfaceFlow == True:
			args[u'subsurface_critical_length_p'] = subsurface_critical_length_p
			args[u'subsurface_eff_p'] = subsurface_eff_p
			args[u'subsurface_critical_length_n'] = subsurface_critical_length_n
			args[u'subsurface_eff_n'] = subsurface_eff_n
		
		if args[u'calc_p'] == True and args[u'calc_n'] == True:
			output_phos = os.path.join(arcpy.env.scratchFolder, _OUTPUT['p_export'])
			outRast.append(output_phos)
			output_nit = os.path.join(arcpy.env.scratchFolder, _OUTPUT['n_export'])
			outRast.append(output_nit)
			#output_watershed = os.path.join(arcpy.env.scratchFolder, _OUTPUT['watershed_results_shp'])

	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
			
	return args, outRast

#Projection alignment issues exist between ArcGIS and InVEST output. This function corrects these issues.	
def DefineProj(raster_ref, raster_out1, raster_out2, shp_ref, shp_out):

	try: 
	
		#get the coordinate system of the raster dem
		dsc = arcpy.Describe(raster_ref)
		coord_sys = dsc.spatialReference
		
		#apply this coordinate system to the output n and p rasters
		rastList = [raster_out1, raster_out2]
		for i in rastList:
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
	args, outRast = GetArgs()
	
	#Run the InVEST script with the arguments from GetArgs
	natcap.invest.ndr.ndr.execute(args)
	
	#Output files from InVEST script
	out_watershed = os.path.join(arcpy.env.scratchFolder, _OUTPUT['watershed_results_shp'])
	out_p = os.path.join(arcpy.env.scratchFolder, outRast[0])
	out_n = os.path.join(arcpy.env.scratchFolder, outRast[1])
	
	#Run the DefineProj function to correct projection alignment issues.
	DefineProj(args['dem_path'], out_p, out_n, args['watersheds_path'], out_watershed)
	
	#Remove intermediate files created by InVEST script
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	
	#Add outputs to map viewer
	arcpy.SetParameter(12, output_watershed)
	arcpy.SetParameter(13, out_p)
	arcpy.SetParameter(14, out_n)
