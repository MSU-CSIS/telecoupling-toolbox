#import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import shutil
import natcap.invest.coastal_blue_carbon.preprocessor

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

#List of output files
_OUTPUT = {
    'carbon_pool_initial_template': r'carbon_pool_initial_template.csv',
    'carbon_pool_transient_template': r'carbon_pool_transient_template.csv',
    'lulc_transitions': r'transitions.csv'
}

#Get the arguments to include in the invest.coastal_blue_carbon.preprocessor model run
def GetArgs():
	lulc_lookup_table = arcpy.GetParameterAsText(0)
	lulc_snapshots = arcpy.GetParameterAsText(1)
	results_suffix = arcpy.GetParameterAsText(2)
	
	outList = []
	
	try:
	
		args = {
			u'lulc_lookup_uri': lulc_lookup_table,
			u'lulc_snapshot_list': lulc_snapshots,
			u'workspace_dir': workspace_dir
		}
		
		
		if results_suffix:
			args[u'results_suffix'] = results_suffix
		
	except Exception:
		e = sys.exc_info()[1]
		arcpy.AddError('An error occurred: {}'.format(e.args[0]))
		
	return args
	
	
if __name__ == '__main__':
	args = GetArgs()
	
	#Run the Nat Cap module
	natcap.invest.coastal_blue_carbon.preprocessor.execute(args)
	
	#Assign Nat Cap model output to variables
	carbon_pool_initial_template = os.path.join(arcpy.env.scratchFolder, _OUTPUT['carbon_pool_initial_template'])
	carbon_pool_transient_template = os.path.join(arcpy.env.scratchFolder, _OUTPUT['carbon_pool_transient_template'])
	lulc_transitions = os.path.join(arcpy.env.scratchFolder, _OUTPUT['lulc_transitions'])
	
	
	#Remove the intermediate folder
	shutil.rmtree(os.path.join(arcpy.env.scratchFolder, 'intermediate_outputs'))
	

	