# Import all necessary module dependencies
import arcpy
import os
import sys

arcpy.env.overwriteOutput = True

def SelectCauses():

    causesLst = arcpy.GetParameterAsText(0)
    causesLst = causesLst.split(";")


    try:

        arcpy.AddMessage(causesLst)

    except Exception:
        e = sys.exc_info()[1]
        arcpy.AddError('An error occurred: {}'.format(e.args[0]))

    #### Set Parameters ####
    arcpy.SetParameterAsText(2, outFile)
    arcpy.ResetProgressor()

if __name__ == '__main__':
    SelectCauses()