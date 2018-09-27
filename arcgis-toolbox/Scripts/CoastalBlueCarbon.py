#Import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import shutil
import natcap.invest.coastal_blue_carbon.coastal_blue_carbon

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder



#Get the arguments to include in the invest.sdr model run
def GetArgs():
	lulc_lookup_table = arcpy.GetParameterAsText(0)
	lulc_transition_effect_of_carbon_table = arcpy.GetParameterAsText(1)
	carbon_pool_initial_variables_table = arcpy.GetParameterAsText(2)
	carbon_pool_transient_variables_table = arcpy.GetParameterAsText(3)
	baseline_raster = arcpy.GetParameterAsText(4)
	year_of_baseline = arcpy.GetParameterAsText(5)
	transition_lulc_raster_list = arcpy.GetParameterAsText(6)
	transition_year_list = arcpy.GetParameterAsText(7)
	do_economic_analysis = arcpy.GetParameterAsText(8)
	use_price_table = arcpy.GetParameterAsText(9)
	price = arcpy.GetParameterAsText(10)
	interest_rate = arcpy.GetParameterAsText(11)
	discount_rate = arcpy.GetParameterAsText(12)
	price_table = arcpy.GetParameterAsText(13)
	analysis_year = arcpy.GetParameterAsText(14)
	
	outList = []
	
	try:
	
		args = {
			#u'analysis_year': year_of_baseline,
			u'carbon_pool_initial_uri': carbon_pool_initial_variables_table,
			u'carbon_pool_transient_uri': carbon_pool_transient_variables_table,
			#u'discount_rate': discount_rater,
			u'do_economic_analysis': do_economic_analysis,
			u'do_price_table': use_price_table,
			#u'interest_rate': interest_rate,
			u'lulc_baseline_map_uri': baseline_raster,
			u'lulc_baseline_year': year_of_baseline,
			u'lulc_lookup_uri': lulc_lookup_table,
			u'lulc_transition_maps_list': transition_lulc_raster_list,
			u'lulc_transition_matrix_uri': lulc_transition_effect_of_carbon_table,
			u'lulc_transition_years_list': transition_year_list,
			u'workspace_dir': workspace_dir,
			
		}
		
		
		if do_economic_analysis:
			if use_price_table:
				args[u'price_table_uri'] = price_table
			else:
				args[u'discount_rate'] = discount_rate
				args[u'interest_rate'] = interest_rate
				args[u'price'] = price
		
		if analysis_year:
			args[u'analysis_year'] = analysis_year
		
		
			
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	return args
	
#List of output files

_OUTPUT = {
    'carbon_stock': 'carbon_stock_at_%s.tif',
    'carbon_accumulation': 'carbon_accumulation_between_%s_and_%s.tif',
    'cabon_emissions': 'carbon_emissions_between_%s_and_%s.tif',
    'carbon_net_sequestration': 'net_carbon_sequestration_between_%s_and_%s.tif',
	'net_present_value': 'net_present_value.tif',
	'total_net_carbon_sequestration': 'total_net_carbon_sequestration.tif',
}
	
if __name__ == '__main__':
	args = GetArgs()
	
	#Run the Nat Cap module
	natcap.invest.coastal_blue_carbon.coastal_blue_carbon.execute(args)
	
	#Assign Nat Cap model output to variables
	carbon_stock = os.path.join(arcpy.env.scratchFolder, _OUTPUT['carbon_stock'])
	carbon_accumulation = os.path.join(arcpy.env.scratchFolder, _OUTPUT['carbon_accumulation'])
	carbon_emissions = os.path.join(arcpy.env.scratchFolder, _OUTPUT['carbon_emissions'])
	carbon_net_sequestration = os.path.join(arcpy.env.scratchFolder, _OUTPUT['carbon_net_sequestration'])
	
	#Remove the intermediate folder
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	
	#Add outputs to map viewer
	arcpy.SetParameter(15, carbon_stock)
	arcpy.SetParameter(16, carbon_accumulation)
	arcpy.SetParameter(17, carbon_emissions)
	arcpy.SetParameter(18, carbon_net_sequestration)
	arcpy.SetParameter(19, net_present_value)
	arcpy.SetParameter(20, total_net_carbon_sequestration)
	
	
