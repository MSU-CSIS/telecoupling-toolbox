# Flow Map Generator tool.  Esri APL July 2013

import arcpy
import os
from arcpy.sa import *
import SSUtilities as UTILS

arcpy.env.overwriteOutput = True
arcpy.env.outputCoordinateSystem = arcpy.SpatialReference(3857)

def isLicensed():
    """Set whether tool is licensed to execute."""
    try:
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            raise Exception
    except:
        return False
    return True

def DrawDistributiveFlows():
    """Execute main script tasks. Draw distributive flow lines"""
    # Assign input parameters to variables
    sourceFC = arcpy.GetParameterAsText(0)
    destinationFC = arcpy.GetParameterAsText(1)
    zField = arcpy.GetParameterAsText(2)
    impassableFC = arcpy.GetParameterAsText(3)
    fgrndFC = arcpy.GetParameterAsText(4)
    destinationWeight = UTILS.getNumericParameter(5)
    sourceWeight = 10 - destinationWeight
    foregroundWeight = UTILS.getNumericParameter(6)
    extstr = arcpy.GetParameterAsText(7)
    c_Size = UTILS.getNumericParameter(8)
    outpolylineFC = os.path.join(arcpy.env.scratchGDB, "DistbFlowLines")
    #outpolyline = arcpy.GetParameterAsText(9)

    if extstr == "Same as Display":
        df = arcpy.mapping.MapDocument("CURRENT").activeDataFrame
        arcpy.env.extent = df.extent
    else:
        #extstr == "Same as Destinations plus Source":
        srcextent = arcpy.Describe(sourceFC).extent
        destextent = arcpy.Describe(destinationFC).extent
        minx = min(srcextent.XMin, destextent.XMin)
        miny = min(srcextent.YMin, destextent.YMin)
        maxx = max(srcextent.XMax, destextent.XMax)
        maxy = max(srcextent.YMax, destextent.YMax)
        arcpy.env.extent = arcpy.Extent(minx, miny, maxx, maxy)

    extlist = arcpy.env.extent

    maxextdim = max(arcpy.env.extent.width, arcpy.env.extent.height)
    desc = arcpy.Describe(sourceFC)
    spatref = desc.spatialReference

    # SliceValue is used to control the magnitude of values in the cost surface and normalize
    # the individual cost surface values so weights have significant effect.
    sliceValue = int(maxextdim / c_Size)
    arcpy.env.cellSize = c_Size

    # -----Make envelope polygon same as processing extent, used later for mask and background fill
    leftEx = str(extlist).split()[0]
    botEx = str(extlist).split()[1]
    rightEx = str(extlist).split()[2]
    topEx = str(extlist).split()[3]
    polyinfo = [[[leftEx, botEx], [leftEx, topEx], [rightEx, topEx], [rightEx, botEx], [leftEx, botEx]]]
    features = []
    for feature in polyinfo:
        features.append(arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in feature]), spatref))
    extenvelope = r"in_memory\temppoly"
    arcpy.CopyFeatures_management(features, extenvelope)
    arcpy.AddMessage("Temporary processing extent feature class created")
    # initialize variables
    impassridge = ""
    impassridge1 = ""
    foregroundras = ""

    # -----If there's an impassable feature, use it to punch holes in the processing envelope mask.
    # -----The impassridge bit below is to create ridges around the impassable holes so flowlines do not flow into the holes later.
    if impassableFC == "":
        polymask = extenvelope
        arcpy.AddMessage("Creating processing mask and background raster")
    else:
        polymask = r"in_memory\pmask"
        impassablepoly = r"in_memory\impasspoly"
        desc = arcpy.Describe(impassableFC)
        # Get the shape type ("Polygon", "Polyline", etc.) of the feature class
        #type = desc.shapeType
        maxeuc = c_Size * 3
        impasseuc = EucDistance(impassableFC, maxeuc, c_Size)
        sliceeuc = Slice(impasseuc, 3, "EQUAL_INTERVAL", 1)
        tfweight = foregroundWeight * 10 * sliceValue
        impassridge1 = 4 - sliceeuc + tfweight
        impassridge = Con(IsNull(impassridge1), 0, impassridge1)
        tinybuf = c_Size / 1.4
        arcpy.Buffer_analysis(impassableFC, impassablepoly, tinybuf, "FULL", "ROUND", "ALL")
        arcpy.Erase_analysis(extenvelope, impassablepoly, polymask)
        arcpy.AddMessage("Creating processing mask and background raster with impassable features")

    mskgrd = r"in_memory\mskgrd"
    arcpy.AddField_management(polymask, "GridVal", "DOUBLE")
    arcpy.CalculateField_management(polymask, "GridVal", "0")
    arcpy.FeatureToRaster_conversion(polymask, "GridVal", mskgrd, c_Size)

    # Set Raster processing mask to the polymask we just created.
    arcpy.env.mask = polymask
    # We now have a processing mask raster with a background value of 0 onto which we will add various cost surfaces.
    # If there are impassable holes in the background  raster they will have ridges around them.

    # ----- Create foreground feature raster and apply foreground weight
    # ----- Foreground weight controls cost to move over foreground features
    if fgrndFC != "":
        fgrdras = r"in_memory\fgrdras"
        fgdesc = arcpy.Describe(fgrndFC)
        if fgdesc.hasOID:
            oidfld = fgdesc.OIDFieldName
            arcpy.FeatureToRaster_conversion(fgrndFC, oidfld, fgrdras)
            tfweight = foregroundWeight * foregroundWeight * sliceValue
            foregroundras = Con(IsNull(fgrdras), mskgrd, tfweight)
            arcpy.AddMessage('Foreground cost raster created')
        else:
            fgrndFC = ""

    # ----- Check Source and destination feature for correct number of features and
    # ----- convert features to points.  These are filterd on input to be polys or points
    desc = arcpy.Describe(sourceFC)
    sourcePoint = r'in_memory\tempsrcpt'
    if desc.shapeType == "Polygon":
        arcpy.FeatureToPoint_management(sourceFC, sourcePoint, "CENTROID")
    else:
        arcpy.CopyFeatures_management(sourceFC, sourcePoint)
    # Check that there's only one source, return error if more than one.
    sourceCount = int(arcpy.GetCount_management(sourcePoint).getOutput(0))
    if sourceCount > 1:
        arcpy.AddError("More than one feature in Source feature class")

    arcpy.AddMessage("Source Feature processed")

    # Describe destination feature class.
    destinationPoints = r'in_memory\destptstemp'
    # Get the shape type ("Polygon", "Polyline", etc.) of the feature class
    desc = arcpy.Describe(destinationFC)
    if desc.shapeType == "Polygon":
        arcpy.FeatureToPoint_management(destinationFC, destinationPoints, "CENTROID")
    else:
        arcpy.CopyFeatures_management(destinationFC, destinationPoints)
    # Remove destinations that have Z-value of NULL or 0 using UpdateCursor.
    with arcpy.da.UpdateCursor(destinationPoints, str(zField)) as cursor:
        for row in cursor:
            if (row[0] is None or row[0] == 0):
                cursor.deleteRow()
    # Check that there's more than one destination.
    destinationCount = int(arcpy.GetCount_management(destinationPoints).getOutput(0))
    # Return error if only one destination.
    if destinationCount == 1:
        arcpy.AddError("Destination feature class only contains one feature.")
    arcpy.AddMessage("Destination features processed")

    try:
        if destinationCount == 0:
            arcpy.AddError("Destination feature class only contains one feature.")
        if sourceCount > 1:
            arcpy.AddError("More than one feature in Source feature class")
        if destinationCount > 1 and sourceCount == 1:
            # ----- Calc euclidean distance from source points, slice into source weight slices
            # ----- This controls how much branching occurs near the source distribution point
            sourceDistanceRaster = EucDistance(sourcePoint)
            sourceSlicedRaster = Slice(sourceDistanceRaster, sliceValue) * sourceWeight
            arcpy.AddMessage('Source cost raster created')

            # ----- Calc euclidean distance from destination points, slice into source weight slices
            # ----- This controls how much distribution lines avoid passing thru destination points
            destinationDistanceRaster = EucDistance(destinationPoints)
            destslice = Slice(destinationDistanceRaster, sliceValue) * destinationWeight
            arcpy.AddMessage("Destination cost raster created")

            # ----- Sum sliced surfaces with forground surface
            if impassableFC != "":
                if fgrndFC != "":
                    sumSlicedRaster = sourceSlicedRaster + destslice + foregroundras + impassridge
                else:
                    sumSlicedRaster = sourceSlicedRaster + destslice + impassridge
            else:
                if fgrndFC != "":
                    sumSlicedRaster = sourceSlicedRaster + destslice + foregroundras
                else:
                    sumSlicedRaster = sourceSlicedRaster + destslice
            arcpy.AddMessage("Total distribution cost raster created")

            initcostbklnk = r"in_memory\initbklnk"
            initcostdist = CostDistance(sourcePoint, sumSlicedRaster, "#", initcostbklnk)
            arcpy.AddMessage('CostDistance and BackLink from source feature calculated')
            # To preserve the CostDistance intermediate raster dataset uncomment the following line
            # arcpy.CopyRaster_management(initcostdist, "CostDistRas")
            # This will write a raster to your default gdb.  If you would rather write a TIF
            # uncomment the next line.  Be sure to supply a full path to where the tif will be written.
            # arcpy.CopyRaster_management(initcostdist, r"mydrive:\mydir_path\CostDistRas.tif")
            # Alter the output raster name and location as required.

            destptras = r"in_memory\destptras"
            arcpy.FeatureToRaster_conversion(destinationPoints, zField, destptras, c_Size)
            destfeatflow = Con(IsNull(destptras), 0, destptras)
            flowdir = r"in_memory\flwdir"
            arcpy.gp.FlowDirection_sa(initcostdist,flowdir,"FORCE","#")
            arcpy.AddMessage('FlowDirection calculated on CostDistance raster')
            flowaccum = r"in_memory\flowaccum"
            arcpy.gp.FlowAccumulation_sa(flowdir, flowaccum, destfeatflow, "INTEGER")
            intflowaccum = Int(Raster(flowaccum))
            flownull = SetNull(intflowaccum, intflowaccum, "VALUE = 0")
            arcpy.AddMessage("FlowAccumulation finished.")

            StreamToFeature(flownull, flowdir, outpolylineFC, "SIMPLIFY")
            arcpy.AddMessage('Finished StreamToFeature')

            arcpy.AddMessage("Data cleanup")
            cleanuplist = [initcostbklnk, initcostdist, destfeatflow, destptras, flowdir, flowaccum, intflowaccum,
                           sumSlicedRaster, destinationDistanceRaster, sourceDistanceRaster, destslice, sourceSlicedRaster,
                           impassridge, impassridge1, fgrdras, foregroundras]
            for ras in cleanuplist:
                if arcpy.Exists(ras):
                    arcpy.Delete_management(ras)
    except:
        outpolylineFC = ""
        # Return the resulting messages as script tool output messages
        for i in xrange(0, arcpy.GetMessageCount()):
            arcpy.AddReturnMessage(i)

    arcpy.SetParameterAsText(9, outpolylineFC)
    arcpy.AddMessage(" ")
    arcpy.AddMessage("NOTE: If script completes with no output make sure Source feature and at least one " \
                          "destination feature is within the processing extent")
    arcpy.AddMessage(" ")


if __name__ == '__main__':
    isLicensed()
    DrawDistributiveFlows()
