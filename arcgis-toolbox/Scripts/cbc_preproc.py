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
    'transitions': r'transitions.csv'
}

#Get the arguments to include in the invest.coastal_blue_carbon.preprocessor model run
def GetArgs():
	lulc_lookup_table = arcpy.GetParameterAsText(0)
	lulc_snapshots = arcpy.GetParameterAsText(1)
	lulc_snapshots = lulc_snapshots.split(";")
	lulc_snapshots = [rast.replace("'","") for rast in lulc_snapshots]
	
	outList = []
	
	try:
	
		args = {
			u'lulc_lookup_uri': lulc_lookup_table,
			u'lulc_snapshot_list': lulc_snapshots,
			u'workspace_dir': workspace_dir
		}
		
		
		
		
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
	transitions = os.path.join(arcpy.env.scratchFolder, _OUTPUT['transitions'])
	
	
