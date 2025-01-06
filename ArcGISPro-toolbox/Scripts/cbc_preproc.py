#import all modules
import arcpy
from arcpy.sa import *
import os
import sys
import shutil
import natcap.invest.coastal_blue_carbon.preprocessor
import natcap.invest.utils

arcpy.env.overwriteOutput = True
workspace_dir = arcpy.env.scratchFolder

#List of output files
_OUTPUT = {
    'Biophysical_Table_Template': r'Biophysical_Table_Template.csv',
    'LULC_Transitions_Template': r'LULC_Transitions_Template.csv',
    'Biophysical_Table_Sample': r'Biophysical_Table_Sample.csv',
    'LULC_Transitions_Sample':r'LULC_Transitions_Sample.csv',
}

#Get the arguments to include in the invest.coastal_blue_carbon.preprocessor model run
def GetArgs():
	lulc_lookup_table = arcpy.GetParameterAsText(0)
	lulc_snapshots = arcpy.GetParameterAsText(1)

	
	outList = []
	
	try:
	
		args = {
			u'lulc_lookup_table_path': lulc_lookup_table,
			u'landcover_snapshot_csv': lulc_snapshots,
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
	Biophysical_Table_Template = os.path.join(arcpy.env.scratchFolder, _OUTPUT['Biophysical_Table_Template'])
	LULC_Transitions_Template = os.path.join(arcpy.env.scratchFolder, _OUTPUT['LULC_Transitions_Template'])
	Biophysical_Table_Sample = os.path.join(arcpy.env.scratchFolder, _OUTPUT['Biophysical_Table_Sample'])
	LULC_Transitions_Sample = os.path.join(arcpy.env.scratchFolder, _OUTPUT['LULC_Transitions_Sample'])
	
	
