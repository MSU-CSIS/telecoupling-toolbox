#This tool maps the flows of commodities from importing and exporting countries.
#Trade data were provided by the Observatory of Economic Complexity
#https://atlas.media.mit.edu/en/resources/permissions/
#Citation: AJG Simoes, CA Hidalgo. The Economic Complexity Observatory: An Analytical Tool for Understanding the Dynamics of Economic Development. 
#          Workshops at the Twenty-Fifth AAAI Conference on Artificial Intelligence. (2011)

#Import modules
import arcpy
import pandas as pd
import os

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def CommodityTrade():
	countrySelection = arcpy.GetParameterAsText(0) #the user's country selection
	commodityData = arcpy.GetParameterAsText(1) #the OEC data set cleaned for the purposes of this tool