#Import all modules
import arcpy
from arcpy.sa import *
import natcap.invest.ndr.ndr
import os
import sys
arcpy.AddMessage("imported modules")

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

_OUTPUT = {
    'watershed_results_shp': r'watershed_results_ndr.shp',
    'p_export': r'p_export.tif',
    'n_export': r'n_export.tif',
}

def GetArgs():
	arcpy.AddMessage("in GetArgs.")
	dem = arcpy.GetParameterAsText(0)
	lulc = arcpy.GetParameterAsText(1)
	nutrient_runoff = arcpy.GetParameterAsText(2)
	watersheds = arcpy.GetParameterAsText(3)
	biophysical_table = arcpy.GetParameterAsText(4)
	threshold_flow_accumulation = arcpy.GetParameterAsText(5)
	k_param = arcpy.GetParameterAsText(6)
#	calc_p = arcpy.GetParameterAsText(7)
#	calc_n = arcpy.GetParameterAsText(8)
	subsurface_critical_length_p = arcpy.GetParameterAsText(7)
	subsurface_critical_length_n = arcpy.GetParameterAsText(8)
	subsurface_eff_p = arcpy.GetParameterAsText(9)
	subsurface_eff_n = arcpy.GetParameterAsText(10)
	
	outList_tabs = []
	
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
		
		
		if args[u'calc_p'] == True:
			args[u'subsurface_critical_length_p'] = subsurface_critical_length_p
			args[u'subsurface_eff_p'] = subsurface_eff_p
			output_phos = os.path.join(arcpy.env.scratchFolder, _OUTPUT['p_export'])
			outList_tabs.append(output_phos)
			output_watershed = os.path.join(arcpy.env.scratchFolder, _OUTPUT['watershed_results_shp'])
			outList_tabs.append(output_watershed)
			
		if args[u'calc_n'] == True:
			args[u'subsurface_critical_length_n'] = subsurface_critical_length_n
			args[u'subsurface_eff_n'] = subsurface_eff_n
			output_nit = os.path.join(arcpy.env.scratchFolder, _OUTPUT['n_export'])
			outList_tabs.append(output_nit)
			
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
			
	return args, outList_tabs
	
	

if __name__ == '__main__':
	args, outList_tabs = GetArgs()
	natcap.invest.ndr.ndr.execute(args)
#	watershed_shp = os.path.join(arcpy.env.scratchFolder, "watershed_results_ndr.shp")  I might not need this line, but I do need the line below it.
#	arcpy.SetParameter(13, watershed_shp)
