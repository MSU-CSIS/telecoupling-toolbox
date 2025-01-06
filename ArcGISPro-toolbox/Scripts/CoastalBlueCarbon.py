#Import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import glob
import shutil
import natcap.invest.coastal_blue_carbon.coastal_blue_carbon

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

_OUTPUT = {
    'carbon_stock': r'carbon-stock-at-',
	'carbon_accumulation': r'carbon-accumulation-between-',
    'carbon_emissions': r'carbon-emissions-between-',
    'carbon_net_sequestration': r'total-net-carbon-sequestration-between-',
	'net_present_value': r'net-present-value.tif',
	'total_net_carbon_sequestration': r'total-net-carbon-sequestration.tif',
}

#Get the arguments to include in the invest.sdr model run
def GetArgs():
	lulc_lookup_table = arcpy.GetParameterAsText(0)
	lulc_snapshots_table = arcpy.GetParameterAsText(1)
	biophysical_table = arcpy.GetParameterAsText(2)
	lulc_transitions_table = arcpy.GetParameterAsText(3)
	baseline_raster = arcpy.GetParameterAsText(4)
	year_of_baseline = arcpy.GetParameterAsText(5)
	transition_lulc_raster_list = arcpy.GetParameterAsText(6)
	transition_lulc_raster_list = transition_lulc_raster_list.split(";")
	transition_lulc_raster_list = [rast.replace("'","") for rast in transition_lulc_raster_list]
	transition_year_list = arcpy.GetParameterAsText(7)
	transition_year_list = transition_year_list.split(";")
	do_economic_analysis = arcpy.GetParameter(8)
	use_price_table = arcpy.GetParameter(9)
	price = float(arcpy.GetParameterAsText(10))
	interest_rate = float(arcpy.GetParameterAsText(11))
	discount_rate = float(arcpy.GetParameterAsText(12))
	price_table = arcpy.GetParameterAsText(13)
	analysis_year = arcpy.GetParameterAsText(14)
	
	outList = []
	
	try:
	
		args = {

                        u'analysis_year':analysis_year,
			u'biophysical_table_path': biophysical_table,
			u'discount_rate': discount_rate,
			u'do_economic_analysis': do_economic_analysis,
                        u'inflation_rate':interest_rate,
			u'landcover_snapshot_csv': lulc_snapshots_table,
			u'landcover_transitions_table': lulc_transitions_table,
			u'price': price,
			u'price_table_path': price_table,
			u'results_suffix': '',
			u'use_price_table': use_price_table,
			u'workspace_dir': workspace_dir,
		}
			
		args_additional = {
                        u'lulc_baseline_year':year_of_baseline,        
			u'lulc_transition_years_list': transition_year_list,
			u'lulc_baseline_map_uri': baseline_raster,

			
		}
		
		if do_economic_analysis:
			args[u'discount_rate']= discount_rate
			if use_price_table:
				args[u'price_table_path'] = price_table
			else:
				args[u'inflation_rate'] = interest_rate
				args[u'price'] = price
		
		if analysis_year:
			args[u'analysis_year'] = analysis_year
		
		
			
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	return args,args_additional
	


def defProj(coord_ref, out_rast):
	
	try:
		#Get the coordinate system of the coordinate reference
		coordSys = arcpy.Describe(coord_ref).spatialReference
		
		arcpy.DefineProjection_management(out_rast, coordSys)
		
	except arcpy.ExecuteError:
		arcpy.AddError(arcpy.GetMessages(2))
		
	except Exception as ex:
		arcpy.AddError(ex.args[0])

	
if __name__ == '__main__':
	args,args_additional = GetArgs()

	#arcpy.AddMessage(args['discount_rate'])
	#arcpy.AddMessage("Test!")
	
	#arcpy.AddMessage(args['lulc_transition_maps_list'])
	#arcpy.AddMessage(args['lulc_lookup_uri'])
	
	year_list = []
	year_list.append(args_additional['lulc_baseline_year'])
	for i in args_additional['lulc_transition_years_list']:
		year_list.append(i)
		
		
	
	#Run the Nat Cap module
	natcap.invest.coastal_blue_carbon.coastal_blue_carbon.execute(args)
	
	
	
	#Assign Nat Cap model output to variables
	carbon_stock_list = []
	carbon_accumulation_list = []
	carbon_emission_list = []
	carbon_net_sequestration_list = []
	for i in range(len(year_list)):
		carbon_stock = os.path.join(arcpy.env.scratchFolder,  "output", _OUTPUT['carbon_stock'] + str(year_list[i]) + '.tif')
		defProj(args_additional[u'lulc_baseline_map_uri'],carbon_stock)
		carbon_stock_list.append(carbon_stock)
		if i < len(year_list)-1:
			carbon_accumulation = os.path.join(arcpy.env.scratchFolder, "output", _OUTPUT['carbon_accumulation'] + str(year_list[i]) + '-and-' + str(year_list[i+1]) + '.tif')
			defProj(args_additional[u'lulc_baseline_map_uri'],carbon_accumulation)
			carbon_accumulation_list.append(carbon_accumulation)
			

			
			carbon_net_sequestration = os.path.join(arcpy.env.scratchFolder, "output", _OUTPUT['carbon_net_sequestration'] + str(year_list[i]) + '-and-' + str(year_list[i+1]) + '.tif')
			defProj(args_additional[u'lulc_baseline_map_uri'],carbon_net_sequestration)
			carbon_net_sequestration_list.append(carbon_net_sequestration)

		if i< len(year_list)-2:
                        carbon_emissions = os.path.join(arcpy.env.scratchFolder, "output", _OUTPUT['carbon_emissions'] + str(year_list[i+1]) + '-and-' + str(year_list[i+2]) + '.tif')
                        defProj(args_additional[u'lulc_baseline_map_uri'],carbon_emissions)
                        carbon_emission_list.append(carbon_emissions)
	net_present_value = os.path.join(arcpy.env.scratchFolder, "output", _OUTPUT['net_present_value'])
	total_net_carbon_sequestration = os.path.join(arcpy.env.scratchFolder, "output", _OUTPUT['total_net_carbon_sequestration'])
	
	
	#os.chdir(os.path.join(arcpy.env.scratchFolder, "outputs_core"))
	#for lyr in glob.glob("*.tif"):
        ##This step is a workaround to correct proj alignment issue in ArcGIS with output from InVEST
		#defProj(args[u'lulc_baseline_map_uri'], lyr)
	#Add outputs to map viewer
	carbon_stock_list = ";".join(carbon_stock_list)
	carbon_accumulation_list = ";".join(carbon_accumulation_list)
	carbon_emission_list = ";".join(carbon_emission_list)
	carbon_net_sequestration_list = ";".join(carbon_net_sequestration_list)
	
	arcpy.SetParameter(15, carbon_stock_list)
	arcpy.SetParameter(16, carbon_accumulation_list)
	arcpy.SetParameter(17, carbon_emission_list)
	arcpy.SetParameter(18, carbon_net_sequestration_list)
	arcpy.SetParameter(19, net_present_value)
	arcpy.SetParameter(20, total_net_carbon_sequestration)
	
	
