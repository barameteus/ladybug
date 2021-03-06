# Outdoor Solar Adjusted Temperature Calculator
# By Chris Mackey
# Chris@MackeyArchitecture.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to adjust an existing Mean Radiant Temperature for shortwave solar radiation.  This adjusted mean radiant temperature can then be used in comfort studies.
_
Note that this component assumes that you have already accounted for longwave radiation in the form of the _meanRadTemperature input.  If you do not hook up a _meanRadTemperature, this component will assume that the surrounding radiant temperature is the same as the air temperature, which is a decent assumption for someone standing in an unobstructed field.  However, the more obstacles that surround the person (and the more "context" that you add), the more important it is to derive a starting mean radiant temperature from a Honeybee Energy simulation.  Also note that this component is not meant to account for shortwave radiation passing through glass.
_
This component uses Radiance functions in order to determine the amount of direct and diffuse solar radiation falling on a comfort mannequin.  The portion reflected off of the ground to the comfort mannequin is derived from these values of direct and diffuse radiation.

Lastly, the formulas to translate this radiation into an effective radiant field and into a solar-adjusted mean radiant temperature come from this paper:
Arens, Edward; Huang, Li; Hoyt, Tyler; Zhou, Xin; Shiavon, Stefano. (2014). Modeling the comfort effects of short-wave solar radiation indoors.  Indoor Environmental Quality (IEQ).
http://escholarship.org/uc/item/89m1h2dg#page-4
-
Provided by Ladybug 0.0.58
    
    Args:
        _location: The location output from the "Ladybug_Import epw" component.
        _cumSkyMtxOrDirNormRad: Either the output from a GenCumulativeSkyMtx component (for high-resolution analysis) or the directNormalRadiation ouput from the "Ladybug_Import epw" component (for simple, low-resolution analsysis).
        _diffuseHorizRad: If you are running a simple analysis with Direct Normal Radiation above, you must provide the diffuseHorizaontalRadiation ouput from the "Ladybug_Import epw" component here.  Otherwise, this input is not required.
        _meanRadTemperature: A number or list of numbers representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  This number will be modified to account for solar radiation.  This input can be air temperature data from the 'Import_epw' component and will follow the assumption that the surrounding mean radiant temperature is the same as the air temperature.  This assumption is ok for a person in an outdoor open field.  However, the more obstacles that surround the person (and the more "contextShading_" that you add), the more important it is to derive a starting mean radiant temperature from a Honeybee Energy simulation.
        -------------------------: ...
        bodyPosture_: An interger between 0 and 5 to set the posture of the comfort mannequin, which can have a large effect on the radiation for a given sun position.  0 = Standing, 1 = Sitting, 2 = Lying Down, 3 = Low-Res Standing, 4 = Low-Res Sitting, and 5 = Low-Res Lying Down.  The default is set to 1 for sitting.
        rotationAngle_: An optional rotation angle in degrees.  Use this number to adjust the angle of the comfort mannequin in space.  The angle of the mannequin in relation to the sun can have a large effect on the amount of radiation that falls on it and thus largely affect the resulting mean radiant temperature.
        bodyLocation_: An optional point that sets the position of the comfort mannequin in space.  Use this to move the comfort mannequin around in relation to contextShading_ connected below. Note that this point should be the center of gravity of your person.  The default is set to a person just above the Rhino origin.
        contextShading_: Optional breps or meshes that represent shading or opaque solar obstructions around the mannequin.  If you are using this component for indoor studies, windows or any transparent materials should not be included in this geometry.  You should factor the transmissivity of these materials in with the windowTransmissivity_ input.  Also, note that, if you have a lot of this context geometry, you should make sure that you input a starting _meanRadTemperature that accounts for the temperature of all the temperture of these shading surfaces.
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        -------------------------: ...
        groundReflectivity_: An optional decimal value between 0 and 1 that represents the fraction of solar radiation reflected off of the ground.  By default, this is set to 0.25, which is characteristic of outdoor grass or dry bare soil.  You may want to increase this value for concrete or decrease it for water or dark soil.
        clothingAbsorptivity_: An optional decimal value between 0 and 1 that represents the fraction of solar radiation absorbed by the human body. The default is set to 0.7 for (average/brown) skin and average clothing.  You may want to increase this value for darker skin or darker clothing.
        windowTransmissivity_: An optional decimal value between 0 and 1 that represents the transmissivity of windows around the person.  This can also be a list of 8760 values between 0 and 1 that represents a list of hourly window transmissivties, in order to represent the effect of occupants pulling blinds over the windows, etc. Note that you should only set a value here if you are using this component for indoor analysis where the only means by which sunlight will hit an occupant is if it comes through a window.  The default is set to 1 for outdoor conditions. 
        -------------------------: ...
        analysisPeriodOrHOY_: An optional analysis period from the Analysis Period component.  If no Analysis period is given, the analysis will be run for the enitre year.
        legendPar_: Optional legend parameters from the Ladybug Legend Parameters component.
        tempOrRad_: Set to 'True' to have the mannequin labled with adjusted perceived radiant temperature and set to 'False' to have the mannequin labled with total radiation falling on the person.
        parallel_: Set to "True" to run the component using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.  For this reason, the default is set to 'True.'
        _runIt: Set to "True" to run the component and calculate solar-adjusted Mean Radiant Temperature.
    Returns:
        readMe!: ...
        --------------------: ...
        effectiveRadiantField: The estimated effective radiant field of the comfort mannequin induced by the sun for each hour of the analysis period.  This is in W/m2.
        MRTDelta: The estimated change in mean radiant temperature for the comfort mannequin induced by the solar radiation.  This is in degreed Celcius.
        solarAdjustedMRT: The estimated solar adjusted mean radiant temperature for each hour of the analysis period.  This is essentially the change in mean radiant temperature above added to the hourly _meanRadTemperature input.  This is in degreed Celcius and can be plugged into any comfort components for comfort studies.
        --------------------: ...
        mannequinMesh: A colored mesh of a comfort mannequin showing the amount of radiation falling over the mannequin's body.
        legend: A legend that corresponds to the colors on the mannequinMesh and shows the relative W/m2.
        legendBasePt: The legend base point, which can be used to move the legend in relation to the chart with the grasshopper "move" component.
        --------------------: ...
        meshFaceResult: If 'tempOrRad' is set to True, this will be the estimated solar adjusted radiant temperature for each mesh face of the mannequin in degrees Celcius.  This radiant temperature is averaged over the the entire analysis period. if 'tempOrRad' is set to False, this will be the total radiation on each mesh face over the analysis period.
        meshFaceArea: The areas of each mesh face of the mannequin in square Rhino model units.  This list corresponds to the meshFaceRadTemp list above and can be used to help inform statistical analysis of the radiant assymmetry over the mannequin.

"""
ghenv.Component.Name = "Ladybug_Outdoor Solar Temperature Adjustor"
ghenv.Component.NickName = 'SolarAdjustTemperature'
ghenv.Component.Message = 'VER 0.0.58\nDEC_11_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "2 | VisualizeWeatherData"
#compatibleLBVersion = VER 0.0.58\nDEC_07_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import Rhino as rc
import scriptcontext as sc
from clr import AddReference
AddReference('Grasshopper')
import Grasshopper.Kernel as gh
import System
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
import math
import System.Threading.Tasks as tasks


inputsDict = {
    
0: ["_location", "The location output from the 'Ladybug_Import epw' component."],
1: ["_cumSkyMtxOrDirNormRad", "Either the output from a GenCumulativeSkyMtx component (for high-resolution analysis) or the directNormallRadiation ouput from the 'Ladybug_Import epw' component (for simple, low-resolution analsysis)."],
2: ["_diffuseHorizRad", "If you are running a simple analysis with Direct Normal Radiation above, you must provide the diffuseHorizaontalRadiation ouput from the 'Ladybug_Import epw' component here.  Otherwise, this input is not required."],
3: ["_meanRadTemperature", "A number or list of numbers representing the mean radiant temperature of the surrounding surfaces in degrees Celcius.  This number will be modified to account for solar radiation.  This input can be air temperature data from the 'Import_epw' component and will follow the assumption that the surrounding mean radiant temperature is the same as the air temperature.  This assumption is ok for a person in an outdoor open field.  However, the more obstacles that surround the person (and the more 'contextShading_' that you add), the more important it is to derive a starting mean radiant temperature from a Honeybee Energy simulation."],
4: ["-------------------------", "..."],
5: ["bodyPosture_", "An interger between 0 and 5 to set the posture of the comfort mannequin, which can have a large effect on the radiation for a given sun position.  0 = Standing, 1 = Sitting, 2 = Lying Down, 3 = Low-Res Standing, 4 = Low-Res Sitting, and 5 = Low-Res Lying Down.  The default is set to 1 for sitting."],
6: ["rotationAngle_", "An optional rotation angle in degrees.  Use this number to adjust the angle of the comfort mannequin in space.  The angle of the mannequin in relation to the sun can have a large effect on the amount of radiation that falls on it and thus largely affect the resulting mean radiant temperature."],
7: ["bodyLocation_", "An optional point that sets the position of the comfort mannequin in space.  Use this to move the comfort mannequin around in relation to contextShading_ connected below. Note that this point should be the center of gravity of your person.  The default is set to a person just above the Rhino origin."],
8: ["contextShading_", "Optional breps or meshes that represent shading or opaque solar obstructions around the mannequin.  If you are using this component for indoor studies, windows or any transparent materials should not be included in this geometry.  You should factor the transmissivity of these materials in with the windowTransmissivity_ input.  Also, note that, if you have a lot of this context geometry, you should make sure that you input a starting _meanRadTemperature that accounts for the temperature of all the temperture of these shading surfaces."],
9: ["north_", "Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees)."],
10: ["-------------------------", "..."],
11: ["groundReflectivity_", "An optional decimal value between 0 and 1 that represents the fraction of solar radiation reflected off of the ground.  By default, this is set to 0.25, which is characteristic of outdoor grass or dry bare soil.  You may want to increase this value for concrete or decrease it for water or dark soil."],
12: ["clothingAbsorptivity_", "An optional decimal value between 0 and 1 that represents the fraction of solar radiation absorbed by the human body. The default is set to 0.7 for (average/brown) skin and average clothing.  You may want to increase this value for darker skin or darker clothing."],
13: ["windowTransmissivity_", "An optional decimal value between 0 and 1 that represents the transmissivity of windows around the person.  This can also be a list of 8760 values between 0 and 1 that represents a list of hourly window transmissivties, in order to represent the effect of occupants pulling blinds over the windows, etc. Note that you should only set a value here if you are using this component for indoor analysis where the only means by which sunlight will hit an occupant is if it comes through a window.  The default is set to 1 for outdoor conditions."],
14: ["-------------------------", "..."],
15: ["analysisPeriodOrHOY_", "An optional analysis period from the 'Analysis Period component' or an hour of the year between 1 and 8760 for which you want to conduct the analysis.  If no analysis period or HOY is given, the analysis will be run for the enitre year."],
16: ["legendPar_", "Optional legend parameters from the Ladybug Legend Parameters component."],
17: ["tempOrRad_", "Set to 'True' to have the mannequin labled with adjusted perceived radiant temperature and set to 'False' to have the mannequin labled with total radiation falling on the person."],
18: ["parallel_", "Set to 'True' to run the component using multiple CPUs.  This can dramatically decrease calculation time but can interfere with other intense computational processes that might be running on your machine.  For this reason, the default is set to 'True.'"],
19: ["_runIt", "The legend base point, which can be used to move the legend in relation to the chart with the grasshopper 'move' component."]
}


outputsDict = {
    
0: ["readMe!", "..."],
1: ["--------------------", "..."],
2: ["effectiveRadiantField", "The estimated effective radiant field of the comfort mannequin induced by the sun for each hour of the analysis period.  This is in W/m2."],
3: ["MRTDelta", "The estimated change in mean radiant temperature for the comfort mannequin induced by the solar radiation.  This is in degreed Celcius."],
4: ["solarAdjustedMRT", "The estimated solar adjusted mean radiant temperature for each hour of the analysis period.  This is essentially the change in mean radiant temperature above added to the hourly _meanRadTemperature input.  This is in degreed Celcius and can be plugged into any comfort components for comfort studies."],
5: ["--------------------", "..."],
6: ["mannequinMesh", "A colored mesh of a comfort mannequin showing the amount of radiation falling over the mannequin's body."],
7: ["legend", "A legend that corresponds to the colors on the mannequinMesh and shows the relative W/m2."],
8: ["legendBasePt", "The input data normalized by the floor area of it corresponding zone."],
9: ["--------------------", "..."],
10: ["meshFaceResult", "If 'tempOrRad' is set to True, this will be the estimated solar adjusted radiant temperature for each mesh face of the mannequin in degrees Celcius.  This radiant temperature is averaged over the the entire analysis period. if 'tempOrRad' is set to False, this will be the total radiation on each mesh face over the analysis period."],
11: ["meshFaceArea", "The areas of each mesh face of the mannequin in square Rhino model units.  This list corresponds to the meshFaceRadTemp list above and can be used to help inform statistical analysis of the radiant assymmetry over the mannequin."]
}


def checkTheInputs():
    # import the classes
    if sc.sticky.has_key('ladybug_release'):
        try:
            if not sc.sticky['ladybug_release'].isCompatible(ghenv.Component): return -1
        except:
            warning = "You need a newer version of Ladybug to use this compoent." + \
            "Use updateLadybug component to update userObjects.\n" + \
            "If you have already updated userObjects drag Ladybug_Ladybug component " + \
            "into canvas and try again."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, warning)
            return -1
            
        lb_preparation = sc.sticky["ladybug_Preparation"]()
        lb_visualization = sc.sticky["ladybug_ResultVisualization"]()
        lb_mesh = sc.sticky["ladybug_Mesh"]()
        lb_runStudy_GH = sc.sticky["ladybug_RunAnalysis"]()
        lb_comfortModels = sc.sticky["ladybug_ComfortModels"]()
        lb_sunpath = sc.sticky["ladybug_SunPath"]()
        
        #Set a default value for epwStr.
        epwStr = []
        
        #Check to see if the user has connected valid MRT data.
        checkData1 = False
        radTemp = []
        if len(_meanRadTemperature) != 0:
            try:
                if "Temperature" in _meanRadTemperature[2]:
                    radTemp = _meanRadTemperature[7:]
                    checkData1 = True
                    epwData = True
                    epwStr = _meanRadTemperature[0:7]
            except: pass
            if checkData1 == False:
                for item in _meanRadTemperature:
                    try:
                        radTemp.append(float(item))
                        checkData1 = True
                    except: checkData1 = False
            if checkData1 == False:
                warning = '_meanRadTemperature input does not contain valid temperature values in degrees Celcius.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            print 'Connect a value for meanRadiantTemperature_.'
            if _runIt == True:
                warning = 'Connect a value for meanRadiantTemperature_.'
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        #If there is only one value for MRT, duplicate it 8760 times.
        if len(radTemp) < 8760 and len(radTemp) !=0:
            if len(radTemp) == 1:
                dupData = []
                for count in range(8760):
                    dupData.append(radTemp[0])
                radTemp = dupData
            else:
                checkData1 = False
                warning = 'Input for _meanRadTemperature must be either the output of an energy simulation, a list of 8760 values, or a single MRT to be applied for every hour of the year.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        #Check to be sure the there is a _cumSkyMtxOrDirNormRad and use it to set the method of the component.
        checkData2 = False
        cumSkyMtx = None
        location = None
        methodInit = 0
        directSolarRad = []
        if len(_cumSkyMtxOrDirNormRad) > 0:
            if _cumSkyMtxOrDirNormRad != [None]:
                if "SkyResultsCollection object" in str(_cumSkyMtxOrDirNormRad[0]):
                    checkData2 = True
                    cumSkyMtx = _cumSkyMtxOrDirNormRad[0]
                    location = cumSkyMtx.location
                elif str(_cumSkyMtxOrDirNormRad[0]) == 'key:location/dataType/units/frequency/startsAt/endsAt':
                    try:
                        if 'Direct Normal Radiation' in _cumSkyMtxOrDirNormRad[2] and len(_cumSkyMtxOrDirNormRad) == 8767:
                            location = _cumSkyMtxOrDirNormRad[1]
                            methodInit = 2
                            checkData2 = True
                            directSolarRad = _cumSkyMtxOrDirNormRad[7:]
                        else:
                            warning = 'Weather data connected to _cumSkyMtxOrDirNormRad is not Direct Normal Radiation or is not hourly data for a full year.'
                            print warning
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    except:
                        warning = 'Invalid value for _cumSkyMtxOrDirNormRad.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                else:
                    warning = 'Invalid value for _cumSkyMtxOrDirNormRad.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else:
                warning = 'Null value connected for _cumSkyMtxOrDirNormRad.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        
        # Get the diffuse Horizontal radiation.
        checkData8 = True
        diffSolarRad = []
        if methodInit == 2:
            try:
                if len(_diffuseHorizRad) > 0:
                    if _diffuseHorizRad != [None]:
                        if str(_diffuseHorizRad[0]) == 'key:location/dataType/units/frequency/startsAt/endsAt':
                            try:
                                if 'Diffuse Horizontal Radiation' in _diffuseHorizRad[2] and len(_diffuseHorizRad) == 8767:
                                    diffSolarRad = _diffuseHorizRad[7:]
                                else:
                                    checkData8 = False
                                    warning = 'Weather data connected to _diffuseHorizRad is not Diffuse Horizontal Radiation or is not hourly data for a full year.'
                                    print warning
                                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                            except:
                                checkData8 = False
                                warning = 'Invalid value for _diffuseHorizRad.'
                                print warning
                                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                        else:
                            checkData8 = False
                            warning = 'Invalid value for _diffuseHorizRad.'
                            print warning
                            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                    else:
                        checkData8 = False
                        warning = 'Null value connected for _diffuseHorizRad.'
                        print warning
                        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
                else:
                    checkData8 = False
            except: pass
        
        #Check the bodyPosture_ input to be sure that it is a valid interger.
        checkData3 = True
        if methodInit == 0:
            if bodyPosture_ == 0 or bodyPosture_ == 1 or bodyPosture_ == 2:
                bodyPosture = bodyPosture_
            elif bodyPosture_ == 3 or bodyPosture_ == 4 or bodyPosture_ == 5:
                bodyPosture = bodyPosture_
                methodInit = 1
            elif bodyPosture_ == None:
                bodyPosture = 1
            else:
                checkData3 = False
                warning = 'Input for bodyPosture_ is not an accepted input interger.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            bodyPosture = -1
        
        
        #Convert the rotation angle to radians or set a default of 0 if there is none.
        rotateAngle = 0.0
        if methodInit != 2:
            try:
                if rotationAngle_ != None: rotateAngle = rotationAngle_*0.0174532925
            except: pass
        
        #Create the comfort mannequin.
        conversionFac = lb_preparation.checkUnits()
        if checkData3 == True and methodInit != 2:
            if bodyPosture == 1:
                mannequinData = lb_comfortModels.getSeatedMannequinData()
            elif bodyPosture == 0 or bodyPosture == 2:
                mannequinData = lb_comfortModels.getStandingMannequinData()
            elif bodyPosture == 4:
                mannequinData = lb_comfortModels.getSeatedMannequinSimple()
            elif bodyPosture == 3 or bodyPosture == 5:
                mannequinData = lb_comfortModels.getStandingMannequinSimple()
            #Construct the mannequin from the point data.
            mannequinMeshBreps = []
            for faceList in mannequinData:
                surfacePts = []
                for pointCoord in faceList:
                    point = rc.Geometry.Point3d(pointCoord[0], pointCoord[1], pointCoord[2])
                    surfacePts.append(point)
                if len(surfacePts) == 4: 
                    surface = rc.Geometry.Brep.CreateFromCornerPoints(surfacePts[0], surfacePts[1], surfacePts[2], surfacePts[3], sc.doc.ModelAbsoluteTolerance)
                else:
                    surface = rc.Geometry.Brep.CreateFromCornerPoints(surfacePts[0], surfacePts[1], surfacePts[2], sc.doc.ModelAbsoluteTolerance)
                mannequinMeshBreps.append(surface)
            mannequinMesh = rc.Geometry.Brep.JoinBreps(mannequinMeshBreps, sc.doc.ModelAbsoluteTolerance)[0]
            #Scale the mannequin based on the model units.
            scale = rc.Geometry.Transform.Scale(rc.Geometry.Plane.WorldXY, 1/conversionFac, 1/conversionFac, 1/conversionFac)
            mannequinMesh.Transform(scale)
            #If the user has selected a mannequin laying down, rotate the standing mannequin.
            if bodyPosture == 2 or bodyPosture == 5:
                lieDownTransform = rc.Geometry.Transform.Rotation(rc.Geometry.Vector3d.ZAxis, rc.Geometry.Vector3d.YAxis, rc.Geometry.Point3d.Origin)
                moveUpTransform = rc.Geometry.Transform.Translation(0,-.85,.15)
                mannequinMesh.Transform(lieDownTransform)
                mannequinMesh.Transform(moveUpTransform)
            else: pass
            #Rotate the mannequin as the user wants.
            if rotateAngle != 0.0:
                rotateTransform = rc.Geometry.Transform.Rotation(rotateAngle, rc.Geometry.Vector3d.ZAxis, rc.Geometry.Point3d.Origin)
                mannequinMesh.Transform(rotateTransform)
            else: pass
            #Change the location of the mannequin as the user wants.
            if bodyLocation_ != None:
                if bodyPosture_ == 0 or bodyPosture_ == 3: moveTransform = rc.Geometry.Transform.Translation(bodyLocation_.X, bodyLocation_.Y, bodyLocation_.Z - 1/conversionFac)
                elif bodyPosture_ == 1 or bodyPosture_ == 4 or bodyPosture_ == None: moveTransform = rc.Geometry.Transform.Translation(bodyLocation_.X, bodyLocation_.Y, bodyLocation_.Z - 0.56/conversionFac)
                else: moveTransform = rc.Geometry.Transform.Translation(bodyLocation_.X, bodyLocation_.Y, bodyLocation_.Z - 0.1/conversionFac)
                mannequinMesh.Transform(moveTransform)
            else: pass
            #Turn the mannequin brep into a mesh.
            mannequinMesh = rc.Geometry.Mesh.CreateFromBrep(mannequinMesh, rc.Geometry.MeshingParameters.Coarse)
        elif methodInit == 2:
            mannequinMesh = []
            #Get a series of 9 points to represent the person, which will be used to calculate the fraction of the body visible to the sun through the context.
            if bodyPosture_ == 0 or bodyPosture_ == 3:
                if bodyLocation_ != None:
                    mannequinAvgHeight = bodyLocation_.Z
                    mannequinX = bodyLocation_.X
                    mannequinY = bodyLocation_.Y
                else:
                    mannequinAvgHeight = 0.85/conversionFac
                    mannequinX = 0
                    mannequinY = 0
                offsetDist = 0.8/conversionFac
                if bodyPosture_ == 0: offsetHeights = [mannequinAvgHeight - offsetDist, (mannequinAvgHeight - offsetDist)+((offsetDist*2)/8), (mannequinAvgHeight - offsetDist)+((offsetDist*4)/8), (mannequinAvgHeight - offsetDist)+((offsetDist*6)/8), mannequinAvgHeight, (mannequinAvgHeight + offsetDist)-((offsetDist*6)/8), (mannequinAvgHeight + offsetDist)-((offsetDist*4)/8), (mannequinAvgHeight + offsetDist)-(offsetDist*2)/8, (mannequinAvgHeight + offsetDist)]
                else: offsetHeights = [mannequinAvgHeight - offsetDist, mannequinAvgHeight, mannequinAvgHeight + offsetDist]
                for height in offsetHeights:
                    mannequinMesh.append(rc.Geometry.Point3d(mannequinX, mannequinY, height))
            elif bodyPosture_ == 1 or bodyPosture_ == 4 or bodyPosture_ == None:
                if bodyLocation_ != None:
                    mannequinAvgHeight = bodyLocation_.Z
                    mannequinX = bodyLocation_.X
                    mannequinY = bodyLocation_.Y
                else:
                    mannequinAvgHeight = 0.65/conversionFac
                    mannequinX = 0
                    mannequinY = 0
                offsetDist = 0.58/conversionFac
                if bodyPosture_ == 1 or bodyPosture_ == None: offsetHeights = [mannequinAvgHeight - offsetDist, (mannequinAvgHeight - offsetDist)+((offsetDist*2)/8), (mannequinAvgHeight - offsetDist)+((offsetDist*4)/8), (mannequinAvgHeight - offsetDist)+((offsetDist*6)/8), mannequinAvgHeight, (mannequinAvgHeight + offsetDist)-((offsetDist*6)/8), (mannequinAvgHeight + offsetDist)-((offsetDist*4)/8), (mannequinAvgHeight + offsetDist)-(offsetDist*2)/8, (mannequinAvgHeight + offsetDist)]
                else: offsetHeights = [mannequinAvgHeight - offsetDist, mannequinAvgHeight, mannequinAvgHeight + offsetDist]
                for height in offsetHeights:
                    mannequinMesh.append(rc.Geometry.Point3d(mannequinX, mannequinY, height))
            else:
                if bodyLocation_ != None:
                    mannequinAvgHeight = bodyLocation_.Z
                    mannequinX = bodyLocation_.X
                    mannequinY = bodyLocation_.Y
                else:
                    mannequinAvgHeight = 0.1
                    mannequinX = 0
                    mannequinY = 0
                offsetDist = 0.8/conversionFac
                if bodyPosture_ == 2: offsetY = [mannequinY - offsetDist, (mannequinY - offsetDist)+((offsetDist*2)/8), (mannequinY - offsetDist)+((offsetDist*4)/8), (mannequinY - offsetDist)+((offsetDist*6)/8), mannequinY, (mannequinY + offsetDist)-((offsetDist*6)/8), (mannequinY + offsetDist)-((offsetDist*4)/8), (mannequinY + offsetDist)-(offsetDist*2)/8, (mannequinY + offsetDist)]
                else: offsetY = [mannequinY - offsetDist, mannequinY, mannequinY + offsetDist]
                for yTrans in offsetY:
                    mannequinMesh.append(rc.Geometry.Point3d(mannequinX, yTrans, mannequinAvgHeight))
                
                if bodyLocation_ != None: mannequinMeshInit = bodyLocation_
                else: mannequinMeshInit = rc.Geometry.Point3d(0,0, 0.1*conversionFac)
                offsetDist = 0.9/conversionFac
        
        #Create a ground mesh.
        if checkData3 == True and methodInit != 2:
            groundMesh = rc.Geometry.Mesh()
            point1 = rc.Geometry.Point3d(-.5, -1, 0)
            point2 = rc.Geometry.Point3d(-.5, -2, 0)
            point3 = rc.Geometry.Point3d(.5, -2, 0)
            point4 = rc.Geometry.Point3d(.5, -1, 0)
            groundMesh.Vertices.Add(point1)
            groundMesh.Vertices.Add(point2)
            groundMesh.Vertices.Add(point3)
            groundMesh.Vertices.Add(point4)
            groundMesh.Faces.AddFace(0, 1, 2, 3)
            if bodyLocation_ != None:
                groundMesh.Transform(moveTransform)
            else: pass
        else:
            groundMesh = None
        
        # Mesh the context.
        if len(contextShading_)!=0:
            ## clean the geometry and bring them to rhinoCommon separated as mesh and Brep
            contextMesh, contextBrep = lb_preparation.cleanAndCoerceList(contextShading_)
            
            ## mesh Brep
            contextMeshedBrep = lb_mesh.parallel_makeContextMesh(contextBrep)
            
            ## Flatten the list of surfaces
            contextMeshedBrep = lb_preparation.flattenList(contextMeshedBrep)
            contextSrfs = contextMesh + contextMeshedBrep
        else: contextSrfs = []
        
        #Check the ground reflectivity.
        checkData4 = True
        if groundReflectivity_ != None:
            if groundReflectivity_ < 1 and groundReflectivity_ > 0:
                groundR = groundReflectivity_
            else:
                groundR = None
                checkData4 = False
                warning = 'groundReflectivity_ must be a value between 0 and 1.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            groundR = 0.25
            print 'No value found for groundReflectivity_.  The ground reflectivity will be set to 0.25 for grass or light bare soil.'
        
        #Check the clothing absorptivity.
        checkData5 = True
        if clothingAbsorptivity_ != None:
            if clothingAbsorptivity_ < 1 and clothingAbsorptivity_ > 0:
                cloA = clothingAbsorptivity_
            else:
                cloA = None
                checkData5 = False
                warning = 'clothingAbsorptivity_ must be a value between 0 and 1.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            cloA = 0.7
            print 'No value found for clothingAbsorptivity_.  The clothing absorptivity will be set to 0.7 for (average/brown) skin and average clothing.'
        
        #Check the windowTransmissivity_.
        checkData6 = True
        winTrans = []
        if windowTransmissivity_ != []:
            if len(windowTransmissivity_) == 8760:
                allGood = True
                for transVal in windowTransmissivity_:
                    transFloat = float(transVal)
                    if transFloat <= 1.0 and transFloat >= 0.0: winTrans.append(transFloat)
                    else: allGood = False
                if allGood == False:
                    checkData6 = False
                    warning = 'windowTransmissivity_ must be a value between 0 and 1.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            elif len(windowTransmissivity_) == 1:
                if windowTransmissivity_[0] <= 1.0 and windowTransmissivity_[0] >= 0.0:
                    for count in range(8760):
                        winTrans.append(windowTransmissivity_[0])
                else:
                    checkData6 = False
                    warning = 'windowTransmissivity_ must be a value between 0 and 1.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            else:
                checkData6 = False
                warning = 'windowTransmissivity_ must be either a list of 8760 values that correspond to hourly changing transmissivity over the year or a single constant value for the whole year.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            for count in range(8760):
                winTrans.append(1)
            print 'No value found for windowTransmissivity_.  The window transmissivity will be set to 1.0 for a fully outdoor calculation.'
        
        #Set the default parallel to true.
        if parallel_ == None: parallel = True
        else: parallel = parallel_
        
        #Make the default analyisis period for the whole year if the user has not input one.
        checkData9 = True
        periodMethod = 0
        if analysisPeriodOrHOY_ == []:
            analysisPeriodOrHOY = [(1, 1, 1), (12, 31, 24)]
        else:
            #Check if the analysis period is an hour of the year or an HOY
            try:
                analysisPeriodOrHOY = int(analysisPeriodOrHOY_[0])
                periodMethod = 1
                if analysisPeriodOrHOY < 1 or analysisPeriodOrHOY > 8760:
                    checkData9 = False
                    warning = 'Hour of the year input for analysisPeriodOrHOY_ must be either a value between 1 and 8760.'
                    print warning
                    ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
            except:
                analysisPeriodOrHOY = analysisPeriodOrHOY_
        
        #Set a north vector if there is not oe already.
        if north_ != None:
            northAngle, northVector = lb_preparation.angle2north(north_)
        else:
            northVector = rc.Geometry.Vector3d.YAxis
            northAngle = 0.0
        
        #Set a default tempOrRad to true.
        try:
            if tempOrRad_ != None: tempOrRad = tempOrRad_
            else: tempOrRad = True
        except: tempOrRad = True
        
        #Set a default rotationAngle to 0.0.
        try:
            if rotationAngle_ != None: rotationAngle = rotationAngle_
            else: rotationAngle = 0.0
        except: rotationAngle = 0.0
        
        #Pull the location data from the inputs.
        checkData7 = True
        latitude = None
        longitude = None
        timeZone = None
        if _location != None:
            try:
                locList = _location.split('\n')
                for line in locList:
                    if "Latitude" in line: latitude = float(line.split(',')[0])
                    elif "Longitude" in line: longitude = float(line.split(',')[0])
                    elif "Time Zone" in line: timeZone = float(line.split(',')[0])
            except:
                checkData7 = False
                warning = 'The connected _location is not a valid location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
                print warning
                ghenv.Component.AddRuntimeMessage(w, warning)
        else:
            checkData7 = False
            print 'Connect a _location from the "Ladybug_Import EWP" component or the "Ladybug_Construct Location" component.'
        
        
        #Check if everything is good.
        if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True and checkData7 == True and checkData8 == True and checkData9 == True:
            checkData = True
        else:
            checkData = False
        
        return checkData, methodInit, radTemp, mannequinMesh, groundMesh, contextSrfs, groundR, cloA, winTrans, parallel, analysisPeriodOrHOY, periodMethod, latitude, longitude, timeZone, rotationAngle, northAngle, northVector, epwStr, conversionFac, cumSkyMtx, directSolarRad, diffSolarRad, location, tempOrRad, lb_preparation, lb_visualization, lb_mesh, lb_runStudy_GH, lb_comfortModels, lb_sunpath
    else:
        return -1


def manageInputOutput(method):
    #If some of the component inputs and outputs are not right, blot them out or change them.
    for input in range(20):
        if input == 2:
            if method == 0 or method == 1:
                ghenv.Component.Params.Input[input].NickName = "."
                ghenv.Component.Params.Input[input].Name = "."
                ghenv.Component.Params.Input[input].Description = " "
            else:
                ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
                ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
        elif input == 16 and method == 2:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        elif input == 17 and method == 2:
            ghenv.Component.Params.Input[input].NickName = "."
            ghenv.Component.Params.Input[input].Name = "."
            ghenv.Component.Params.Input[input].Description = " "
        else:
            ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
            ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    for output in range(12):
        if output == 7 or output == 8 or output == 10 or output == 11:
            if method == 2:
                ghenv.Component.Params.Output[output].NickName = "."
                ghenv.Component.Params.Output[output].Name = "."
                ghenv.Component.Params.Output[output].Description = " "
            else:
                ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
                ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
                ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
        else:
            ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
            ghenv.Component.Params.Output[output].Description = outputsDict[output][1]
    
    return True

def restoreInputOutput():
    for input in range(19):
        ghenv.Component.Params.Input[input].NickName = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Name = inputsDict[input][0]
        ghenv.Component.Params.Input[input].Description = inputsDict[input][1]
    
    for output in range(12):
        ghenv.Component.Params.Output[output].NickName = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Name = outputsDict[output][0]
        ghenv.Component.Params.Output[output].Description = outputsDict[output][1]



def runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH):
    RADIANCE_radiationStudy = []
    if len(RADIANCE_radiationStudy)!=0:
        pass
    elif cumSky_radiationStudy != None and (len(cumSky_radiationStudy) == 456 or len(cumSky_radiationStudy) == 1752) and analysisSrfs:
        indexList, listInfo = lb_preparation.separateList(cumSky_radiationStudy, lb_preparation.strToBeFound)
        selList = []
        for i in range(1):
            [selList.append(float(x)) for x in cumSky_radiationStudy[indexList[i]+7:indexList[i+1]]]
            
        cumSky_radiationStudy = selList
        if parallel:
            try:
                for geo in analysisSrfs + contextSrfs: geo.EnsurePrivateCopy()
            except:
                pass
        
        # join the meshes
        joinedAnalysisMesh = lb_mesh.joinMesh(analysisSrfs)
        if contextSrfs: joinedContext = lb_mesh.joinMesh(contextSrfs)
        else: joinedContext = None
        if len(cumSky_radiationStudy) == 145:
            radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                    parallel, cumSky_radiationStudy, lb_preparation.TregenzaPatchesNormalVectors, conversionFac, 2200000000000000, northVector)
        elif len(cumSky_radiationStudy) == 577:
            radResults, totalRadResults, intersectionMtx = lb_runStudy_GH.parallel_radCalculator(testPoints, ptsNormals, meshSrfAreas, joinedAnalysisMesh, joinedContext,
                                    parallel, cumSky_radiationStudy, lb_preparation.getReinhartPatchesNormalVectors(), conversionFac, 2200000000000000, northVector)
                                    
    
    return radResults, totalRadResults, listInfo, intersectionMtx

def getHourlySky(daylightMtxDict, HOY):
    # for presentation
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    stDate = lb_preparation.hour2Date(HOY, 1)
    analysisP = ((stDate[1]+1, stDate[0], stDate[2]-1),(stDate[1]+1, stDate[0], stDate[2]))
    
    hourlyMtx = []
    for patchNumber in daylightMtxDict.keys():
        # first patch is the ground
        if patchNumber!=0:
            hourlyMtx.append(daylightMtxDict[patchNumber][HOY])
    return hourlyMtx, analysisP

def getCumulativeSky(daylightMtxDict, runningPeriod):
    
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    def selectHourlyData(dataList, analysisPeriodOrHOY):
        # read analysis period
        stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriodOrHOY, False)
        
        selHourlyData =[];
        
        # select data
        stAnnualHour = lb_preparation.date2Hour(stMonth, stDay, stHour)
        endAnnualHour = lb_preparation.date2Hour(endMonth, endDay, endHour)
        
        # check it goes from the end of the year to the start of the year
        if stAnnualHour < endAnnualHour:
            for i, item in enumerate(dataList[stAnnualHour-1:endAnnualHour+1]):
                if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
            type = True
        else:
            for i, item in enumerate(dataList[stAnnualHour-1:]):
                if stHour-1 <= (i + stHour - 1)%24 <= endHour-1: selHourlyData.append(item)
            for i, item in enumerate(dataList[:endAnnualHour + 1]):
                if stHour-1 <= i %24 <= endHour-1: selHourlyData.append(item)
            type = False
        
        return selHourlyData
    
    HOYS = selectHourlyData(range(8760), runningPeriod)
    
    hourlyMtx = []
    for patchNumber in daylightMtxDict.keys():
        if patchNumber!=0:
            cumulativeDifValue = 0
            cumulativeDirValue = 0
            # adding upp the values
            try:
                for HOY in HOYS:
                    difValue, dirValue = daylightMtxDict[patchNumber][HOY + 1]
                    cumulativeDifValue += difValue
                    cumulativeDirValue += dirValue 
            except Exception, e:
                print `e`
                
            hourlyMtx.append([cumulativeDifValue/1000, cumulativeDirValue/1000])
    
    return hourlyMtx

def prepareLBList(skyMtxLists, analysisPeriodOrHOY, locName, unit, removeDiffuse, removeDirect):
    lb_preparation = sc.sticky["ladybug_Preparation"]()
    
    # prepare the final output
    stMonth, stDay, stHour, endMonth, endDay, endHour = lb_preparation.readRunPeriod(analysisPeriodOrHOY, False)
    totalRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Total Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    diffuseRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Diffuse Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    directRad = [lb_preparation.strToBeFound, locName, "Sky Patches' Direct Radiation", unit, 'NA', (stMonth, stDay, stHour), (endMonth, endDay, endHour)]
    
    for radValues in skyMtxLists:
        if not removeDiffuse and not removeDirect:
            totalRad.append(sum(radValues))
            diffuseRad.append(radValues[0])
            directRad.append(radValues[1])
        elif removeDiffuse and removeDirect:
            totalRad.append(0)
            diffuseRad.append(0)
            directRad.append(0)
        elif removeDirect:
            totalRad.append(radValues[0])
            diffuseRad.append(radValues[0])
            directRad.append(0)
        elif removeDiffuse:
            totalRad.append(radValues[1])
            diffuseRad.append(0)
            directRad.append(radValues[1])
    
    return totalRad + diffuseRad + directRad

def resultVisualization(analysisSrfs, results, totalResults, legendPar, legendTitle, studyLayerName, checkTheName, l, listInfo, lb_preparation, lb_visualization):
    
    lowB, highB, numSeg, customColors, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold = lb_preparation.readLegendParameters(legendPar, False)
    
    colors = lb_visualization.gradientColor(results, lowB, highB, customColors)
    
    # color mesh surfaces
    analysisSrfs = lb_visualization.colorMesh(colors, analysisSrfs)
    
    ## generate legend
    # calculate the boundingbox to find the legendPosition
    personGeo = analysisSrfs.DuplicateMesh()
    personGeo.Faces.DeleteFaces([len(results)-1])
    if sc.doc.ModelAbsoluteTolerance < 0.001: lb_visualization.calculateBB([personGeo])
    elif sc.doc.ModelAbsoluteTolerance < 0.05:
        initBoundBox = rc.Geometry.Mesh.GetBoundingBox(personGeo, rc.Geometry.Plane.WorldXY)
        scalePlane = rc.Geometry.Plane(initBoundBox.Min, rc.Geometry.Vector3d.ZAxis)
        scaleTrans = rc.Geometry.Transform.Scale(scalePlane, 1.5, 1.5, 1.5)
        initBoundBox.Transform(scaleTrans)
        finBBox = initBoundBox.ToBrep()
        lb_visualization.calculateBB([finBBox])
    else:
        warning = 'Your Rhino model tolerance is not small enough and this will cause the legend text to display weirdly or the text function to fail.'
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        initBoundBox = rc.Geometry.Mesh.GetBoundingBox(personGeo, rc.Geometry.Plane.WorldXY)
        scalePlane = rc.Geometry.Plane(initBoundBox.Min, rc.Geometry.Vector3d.ZAxis)
        scaleTrans = rc.Geometry.Transform.Scale(scalePlane, 2, 2, 2)
        initBoundBox.Transform(scaleTrans)
        finBBox = initBoundBox.ToBrep()
        lb_visualization.calculateBB([finBBox])
    
    # legend geometry
    legendSrfs, legendText, legendTextCrv, textPt, textSize = lb_visualization.createLegend(results, lowB, highB, numSeg, legendTitle, lb_visualization.BoundingBoxPar, legendBasePoint, legendScale, legendFont, legendFontSize, legendBold)
    
    # legend colors
    legendColors = lb_visualization.gradientColor(legendText[:-1], lowB, highB, customColors)
    # color legend surfaces
    legendSrfs = lb_visualization.colorMesh(legendColors, legendSrfs)

    customHeading = '\n\nSolar Adjusted Radiant Temperature'
    titleTextCurve, titleStr, titlebasePt = lb_visualization.createTitle([listInfo[0]], lb_visualization.BoundingBoxPar, legendScale, customHeading, False, legendFont, legendFontSize, legendBold)
    
    if legendBasePoint == None: legendBasePoint = lb_visualization.BoundingBoxPar[0]
    
    
    return analysisSrfs, [legendSrfs, lb_preparation.flattenList(legendTextCrv + titleTextCurve)], l, legendBasePoint


def convertFluxToTemp(radiantFlux, cloA, fracEff, radTransCoeff, currentRT, avgWinTrans, energyConvertFac):
    newFlux = avgWinTrans*radiantFlux*energyConvertFac
    ERFsolar = (newFlux * cloA)/0.95
    avgRTDelt = (ERFsolar/(fracEff*radTransCoeff))
    avgRT = currentRT + avgRTDelt
    
    return avgRT


def main(method, radTemp, mannequinMesh, groundMesh, contextSrfs, groundR, cloA, winTrans, parallel, analysisPeriodOrHOY, periodMethod, latitude, longitude, timeZone, northAngle, northVector, epwStr, conversionFac, cumSkyMtx, location, tempOrRad, lb_preparation, lb_visualization, lb_mesh, lb_runStudy_GH, lb_comfortModels, lb_sunpath):
    #Define lists to be filled and put headers on them.
    ERF = []
    MRTDelta = []
    solarAdjustedMRT = []
    hourOrder = []
    
    #Define the fraction of the body visible to radiation.
    if bodyPosture_ == 0 or bodyPosture_ == 3:
        fracEff = 0.725
    elif bodyPosture_ == 1 or bodyPosture_ == 4 or bodyPosture_ == None:
        fracEff = 0.696
    else:
        fracEff = 0.68
    
    #Define a good guess of a radiative heat transfer coefficient.
    radTransCoeff = 6.012
    
    #Get a list of HOYs for the analysis period
    if periodMethod == 0: HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriodOrHOY, 1)
    else: HOYS = [analysisPeriodOrHOY]
    
    #Compute the existing ERF for the analysis period.
    if analysisPeriodOrHOY != [(1, 1, 1), (12, 31, 24)]:
        newAirTemp = []
        newRadTemp = []
        for hour in HOYS:
            newRadTemp.append(radTemp[hour-1])
        radTemp = newRadTemp
    
    #Calculate the sun-up hours of the year to help make things faster down the road.
    lb_sunpath.initTheClass(float(latitude), northAngle, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
    altitudes = []
    finalWinTransmiss = []
    for hour in HOYS:
        d, m, t = lb_preparation.hour2Date(hour, True)
        lb_sunpath.solInitOutput(m+1, d, t)
        altitude = lb_sunpath.solAlt
        altitudes.append(altitude)
        finalWinTransmiss.append(winTrans[hour-1])
    
    #Process the cumulative sky into an initial selected sky.
    skyMtxLists = []
    if periodMethod == 0: skyMtxLists = getCumulativeSky(cumSkyMtx.d, analysisPeriodOrHOY)
    else: skyMtxLists, analysisPeriodTxt = getHourlySky(cumSkyMtx.d, analysisPeriodOrHOY)
    
    #Set a unit for the analysis.
    if len(HOYS) == 1: unit = 'Wh'
    else: unit = 'kWh'
    
    if len(skyMtxLists)!=0:
        if periodMethod == 0: selectedSkyMtx = prepareLBList(skyMtxLists, analysisPeriodOrHOY, location, unit, False, False)
        else: selectedSkyMtx = prepareLBList(skyMtxLists, analysisPeriodTxt, location, unit, False, False)
        cumSky_radiationStudy = selectedSkyMtx
        
        #Set defaults.
        disFromBase = 0.01
        analysisSrfs = []
        for mesh in mannequinMesh:
             analysisSrfs.append(mesh)
        analysisSrfs.append(groundMesh)
        
        ## extract test points
        testPoints, ptsNormals, meshSrfAreas = lb_mesh.parallel_testPointCalculator(analysisSrfs, float(disFromBase), parallel)
        originalTestPoints = testPoints
        testPoints = lb_preparation.flattenList(testPoints)
        
        ptsNormals = lb_preparation.flattenList(ptsNormals)
        meshSrfAreas = lb_preparation.flattenList(meshSrfAreas)
        
        #Get an intersection matrix of the geometry and the sky and some results for the whole analysis period.
        radResults, totalRadResults, listInfo, intersectionMtx = runAnalyses(testPoints, ptsNormals, meshSrfAreas, analysisSrfs, contextSrfs, parallel, cumSky_radiationStudy, conversionFac, northVector, lb_preparation, lb_mesh, lb_runStudy_GH)
        
        #Convert Rad results to radiant temperature.
        if tempOrRad == True:
            unit = 'C'
            avgWinTrans = sum(finalWinTransmiss)/len(finalWinTransmiss)
            currentRT = sum(radTemp)/len(radTemp)
            meshResults = []
            for count, flux in enumerate(radResults):
                if periodMethod == 0: energyConvertFac = 500
                else: energyConvertFac = 1
                avgFlux = flux/len(radTemp)
                convertRadTemp = convertFluxToTemp(avgFlux, cloA, fracEff, radTransCoeff, currentRT, avgWinTrans, energyConvertFac)
                meshResults.append(convertRadTemp)
        else: meshResults = radResults
        
        #Make a colored mesh of the mannequin for the whole analysis period.
        resultColored = []
        legendColored = []
        studyLayerNames = "RADIATION_STUDIES"
        
        if radResults!= None:
            resultColored, legendColored, l, legendBasePoint = resultVisualization(analysisSrfs, meshResults, totalRadResults, legendPar_, unit, studyLayerNames, True, 0, listInfo, lb_preparation, lb_visualization)
        
        #Remove the ground mesh, which is the last one.
        resultColored.Faces.DeleteFaces([len(radResults)-1])
        
        #Unpack the legend.
        legend = []
        legend.append(legendColored[0])
        for item in legendColored[1]:
            legend.append(item)
        
        intDict = intersectionMtx
        personMeshAreas = []
        for area in meshSrfAreas[:-1]:
            personMeshAreas.append(area*conversionFac*conversionFac)
        if method == 0:
            totalPersonArea = sum(personMeshAreas)
        elif method == 1:
            totalPersonArea = 1.775
        
        
        #Define functions for computing the radiation for each hour, which is in parallal and not in parallel.
        def nonParallelRadCalc():
            for count, hour in enumerate(HOYS):
                if count != len(HOYS)-1: lastVal = 1
                else: lastVal = 0
                if altitudes[count] > 0 or altitudes[count-1] > 0 or altitudes[count+lastVal] > 0:
                    skyMtxLists, _analysisPeriodOrHOY_ = getHourlySky(cumSkyMtx.d, hour)
                    selSkyMatrix = prepareLBList(skyMtxLists, _analysisPeriodOrHOY_, location, unit, False, False)
                    
                    indexList, listInfo = lb_preparation.separateList(selSkyMatrix, lb_preparation.strToBeFound)
                    #separate total, diffuse and direct radiations
                    separatedLists = []
                    for i in range(len(indexList)-1):
                        selList = []
                        [selList.append(float(x)) for x in selSkyMatrix[indexList[i] + 7:indexList[i+1]]]
                        separatedLists.append(selList)
                    
                    skyMatrix = separatedLists[0]
                    
                    radiationResult = []
                    for ptCount in  intDict.keys():
                        radValue = 0
                        for patchCount in intDict[ptCount].keys():
                            if intDict[ptCount][patchCount]['isIntersect']:
                                radValue = radValue + (skyMatrix[patchCount] * math.cos(intDict[ptCount][patchCount]['vecAngle']))
                        radiationResult.append(radValue)
                    
                    personRad = radiationResult[:-1]
                    groundRad = radiationResult[-1]
                    totalPersonBeamDiffRad = sum([a*b for a,b in zip(personRad,personMeshAreas)])
                    
                    #Account for the transmissivity of glass.
                    if finalWinTransmiss[count] != 1:
                        groundRad = groundRad*(finalWinTransmiss[count])
                        totalPersonBeamDiffRad = totalPersonBeamDiffRad*(finalWinTransmiss[count])
                    
                    #Calculate the additional radiation reflected to the person by the ground.
                    groundRefRad = 0.5 * groundRad * fracEff * groundR
                    
                    #Calculate the total person radiation and the ERF.
                    totalPersonRad = totalPersonBeamDiffRad + groundRefRad
                    radiantFlux = totalPersonRad/totalPersonArea
                    hourERF = (radiantFlux * cloA)/0.95
                    ERF.append(hourERF/1000)
                    
                    #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                    hourMRT = (hourERF/(fracEff*radTransCoeff)) + (radTemp[count])
                    solarAdjustedMRT.append(hourMRT)
                    mrtDelt = hourMRT - radTemp[count]
                    MRTDelta.append(mrtDelt)
                else:
                    ERF.append(0)
                    solarAdjustedMRT.append(radTemp[count])
                    MRTDelta.append(0)
            return True
        
        def parallelRadCalc():
            def radCalc(count):
                if count != len(HOYS)-1: lastVal = 1
                else: lastVal = 0
                if altitudes[count] > 0 or altitudes[count-1] > 0 or altitudes[count+lastVal] > 0:
                    skyMtxLists, _analysisPeriodOrHOY_ = getHourlySky(cumSkyMtx.d, HOYS[count])
                    selSkyMatrix = prepareLBList(skyMtxLists, _analysisPeriodOrHOY_, location, unit, False, False)
                    
                    indexList, listInfo = lb_preparation.separateList(selSkyMatrix, lb_preparation.strToBeFound)
                    #separate total, diffuse and direct radiations
                    separatedLists = []
                    for i in range(len(indexList)-1):
                        selList = []
                        [selList.append(float(x)) for x in selSkyMatrix[indexList[i] + 7:indexList[i+1]]]
                        separatedLists.append(selList)
                    
                    skyMatrix = separatedLists[0]
                    
                    radiationResult = []
                    for ptCount in  intDict.keys():
                        radValue = 0
                        for patchCount in intDict[ptCount].keys():
                            if intDict[ptCount][patchCount]['isIntersect']:
                                radValue = radValue + (skyMatrix[patchCount] * math.cos(intDict[ptCount][patchCount]['vecAngle']))
                        radiationResult.append(radValue)
                    
                    personRad = radiationResult[:-1]
                    groundRad = radiationResult[-1]
                    totalPersonBeamDiffRad = sum([a*b for a,b in zip(personRad,personMeshAreas)])
                    
                    #Account for the transmissivity of glass.
                    if (finalWinTransmiss[count]) != 1:
                        groundRad = groundRad*(finalWinTransmiss[count])
                        totalPersonBeamDiffRad = totalPersonBeamDiffRad*(finalWinTransmiss[count])
                    
                    #Calculate the additional radiation reflected to the person by the ground.
                    groundRefRad = 0.5 * groundRad * fracEff * groundR
                    
                    #Calculate the total person radiation and the ERF.
                    totalPersonRad = totalPersonBeamDiffRad + groundRefRad
                    radiantFlux = totalPersonRad/totalPersonArea
                    hourERF = (radiantFlux * cloA)/0.95
                    ERF.append(hourERF/1000)
                    
                    #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                    hourMRT = (hourERF/(fracEff*radTransCoeff)) + (radTemp[count])
                    solarAdjustedMRT.append(hourMRT)
                    mrtDelt = hourMRT - radTemp[count]
                    MRTDelta.append(mrtDelt)
                else:
                    ERF.append(0)
                    solarAdjustedMRT.append(radTemp[count])
                    MRTDelta.append(0)
                hourOrder.append(count)
            
            tasks.Parallel.ForEach(range(len(HOYS)), radCalc)
            
            return True
        
        # Compute the radiation for each hour of the year.
        if parallel == False:
            runSuccess = nonParallelRadCalc()
        else:
            runSuccess = parallelRadCalc()
        
        #If the process above was run in parallel, re-order the numbers correctly (instead of by when they finished calculating).
        if parallel == True:
            ERF = [x for (y,x) in sorted(zip(hourOrder, ERF))]
            MRTDelta = [x for (y,x) in sorted(zip(hourOrder, MRTDelta))]
            solarAdjustedMRT = [x for (y,x) in sorted(zip(hourOrder, solarAdjustedMRT))]
        
        
        #Add the headers to the computed lists.
        if periodMethod == 0:
            analysisStart = analysisPeriodOrHOY[0]
            analysisEnd = analysisPeriodOrHOY[1]
        else:
            analysisStart = analysisPeriodTxt[0]
            analysisEnd = analysisPeriodTxt[1]
        
        ERF.insert(0,analysisEnd)
        ERF.insert(0,analysisStart)
        ERF.insert(0,'Hourly')
        ERF.insert(0,'kWh/m2')
        ERF.insert(0,'Effective Radiant Field')
        ERF.insert(0,str(location))
        ERF.insert(0,'key:location/dataType/units/frequency/startsAt/endsAt')
        
        MRTDelta.insert(0,analysisEnd)
        MRTDelta.insert(0,analysisStart)
        MRTDelta.insert(0,'Hourly')
        MRTDelta.insert(0,'C')
        MRTDelta.insert(0,'Solar Mean Radiant Temp Delta')
        MRTDelta.insert(0,str(location))
        MRTDelta.insert(0, 'key:location/dataType/units/frequency/startsAt/endsAt')
        
        solarAdjustedMRT.insert(0,analysisEnd)
        solarAdjustedMRT.insert(0,analysisStart)
        solarAdjustedMRT.insert(0,'Hourly')
        solarAdjustedMRT.insert(0,'C')
        solarAdjustedMRT.insert(0,'Solar-Adjusted Mean Radiant Temperature')
        solarAdjustedMRT.insert(0,str(location))
        solarAdjustedMRT.insert(0,'key:location/dataType/units/frequency/startsAt/endsAt')
        
        
        return ERF, MRTDelta, solarAdjustedMRT, resultColored, legend, legendBasePoint, meshResults, meshSrfAreas
    else:
        return None, None, None, None, None, None
        warning = "cumulativeSkyMtx failed to collect data."
        print warning
        ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)


def mainSimple(radTemp, mannequinMesh, context, groundR, cloA, winTrans, analysisPeriodOrHOY, periodMethod, latitude, longitude, timeZone, rotationAngle, northAngle, northVector, epwStr, directSolarRad, diffSolarRad, location, parallel, lb_preparation, lb_comfortModels, lb_sunpath):
    #Define lists to be filled and put headers on them.
    ERF = []
    MRTDelta = []
    solarAdjustedMRT = []
    hourOrder = []
    
    #Define the fraction of the body visible to radiation.
    if bodyPosture_ == 0 or bodyPosture_ == 3:
        fracEff = 0.725
    elif bodyPosture_ == 1 or bodyPosture_ == 4 or bodyPosture_ == None:
        fracEff = 0.696
    else:
        fracEff = 0.68
    
    #Define a good guess of a radiative heat transfer coefficient.
    radTransCoeff = 6.012
    
    #Get a list of HOYs for the analysis period
    if periodMethod == 0: HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriodOrHOY, 1)
    else: HOYS = [analysisPeriodOrHOY]
    
    #Compute the existing ERF for the analysis period.
    if analysisPeriodOrHOY != [(1, 1, 1), (12, 31, 24)]:
        newAirTemp = []
        newRadTemp = []
        for hour in HOYS:
            newRadTemp.append(radTemp[hour-1])
        radTemp = newRadTemp
    
    #Calculate the skyview factor of the occupant.
    if bodyPosture_ == None or bodyPosture_ == 0 or bodyPosture_ == 1 or bodyPosture_ == 2: middlePt = mannequinMesh[4]
    else: middlePt = mannequinMesh[1]
    
    if len(context) > 0:
        viewVectors = []
        viewTuples = lb_preparation.TregenzaPatchesNormalVectors
        for tuple in viewTuples:
            viewVectors.append(rc.Geometry.Vector3d(tuple[0], tuple[1], tuple[2]))
        totalVecNum = len(viewVectors)
        vecBlockedList = []
        for viewVec in viewVectors:
            viewRay = rc.Geometry.Ray3d(middlePt, viewVec)
            viewBlocked = False
            for mesh in context:
                rayIntersect = rc.Geometry.Intersect.Intersection.MeshRay(mesh, viewRay)
                if rayIntersect > 0: viewBlocked = True
            if viewBlocked == True: vecBlockedList.append(1)
        skyViewFac = 1 - sum(vecBlockedList)/totalVecNum
    else: skyViewFac = 1
    
    #Calculate the sun-up hours of the year in order to understand whether the context geometry will block the sun.
    lb_sunpath.initTheClass(float(latitude), northAngle, rc.Geometry.Point3d.Origin, 100, float(longitude), float(timeZone))
    altitudes = []
    azimuths = []
    sunVectors = []
    for hour in HOYS:
        d, m, t = lb_preparation.hour2Date(hour, True)
        lb_sunpath.solInitOutput(m+1, d, t)
        altitude = lb_sunpath.solAlt
        altitudes.append(altitude)
        azimuths.append(lb_sunpath.solAz)
        if altitude > 0:
            sunVec = lb_sunpath.sunReverseVectorCalc()
            sunVectors.append(sunVec)
        else: sunVectors.append(None)
    
    #Compute all of the outputs.
    def nonParallelMRTCalc():
        for count, hour in enumerate(HOYS):
            if altitudes[count] > 0:
                #Calculate fBes, the fraction of the body that is visible to the sun and is not blocked by the context.
                if len(context) > 0:
                    #First get the sunRays.
                    sunRays = []
                    for point in mannequinMesh:
                        sunRay = rc.Geometry.Ray3d(point, sunVectors[count])
                        sunRays.append(sunRay)
                    
                    #Next check how many of the sunrays are blocked.
                    fBesList = []
                    for ray in sunRays:
                        sunBlocked = False
                        for mesh in context:
                            rayIntersect = rc.Geometry.Intersect.Intersection.MeshRay(mesh, ray)
                            if rayIntersect > 0: sunBlocked = True
                        if sunBlocked == False:fBesList.append(1)
                        else: fBesList.append(0)
                    
                    #Finally, calculate Fbes from that which was blocked.
                    fBes = sum(fBesList)/len(fBesList)
                else:
                    fBes = 1
                
                if fBes > 0.0:
                    #Calculate the diffuse, direct, and global horizontal components of the solar radiation.
                    diffRad = diffSolarRad[hour-1]
                    dirNormRad = directSolarRad[hour-1]
                    globHorizRad = dirNormRad*(math.sin(altitudes[count])) + diffRad
                    
                    #Define the Azimuth as the SolarCal function understands it.
                    azInit = math.degrees(azimuths[count])
                    #Change the azimuth based on the north angle and the rotation angle of the mannequin.
                    if northAngle != 0.0: azInit = azInit + northAngle
                    if rotationAngle != 0.0: azInit = azInit + rotationAngle
                    
                    #Compute a final Azimuth that can be put through the spline function.
                    azFinal = azInit
                    if azInit > 180:
                        while azFinal > 180:
                            azFinal = azFinal-180
                    elif azInit < 0:
                        while azFinal < 0:
                            azFinal = azFinal+180
                    azFinal = int(azFinal)
                    
                    #Define the Altitude as the SolarCal function understands it.
                    altInit = int(math.degrees(altitudes[count]))
                    if altInit > 90: altFinal = altInit-90
                    else: altFinal = altInit
                    
                    #Calculate the projected area factor from the altitude and azimuth.
                    if bodyPosture_ == 0 or bodyPosture_ == 3:
                        ProjAreaFac = lb_comfortModels.splineStand(azFinal, altFinal)
                    elif bodyPosture_ == 1 or bodyPosture_ == 4 or bodyPosture_ == None:
                        ProjAreaFac = lb_comfortModels.splineSit(azFinal, altFinal)
                    else:
                        ProjAreaFac = lb_comfortModels.splineStand(azFinal, 90-altFinal)
                    
                    # Calculate the ERF of the occupant
                    hourERF = ((0.5*fracEff*skyViewFac*(diffRad + (globHorizRad*groundR))+ (fracEff*ProjAreaFac*fBes*dirNormRad))*winTrans[hour-1])*(cloA/0.95)
                    
                    ERF.append(hourERF)
                    #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                    mrtDelt = (hourERF/(fracEff*radTransCoeff))
                    MRTDelta.append(mrtDelt)
                    hourMRT = mrtDelt + (radTemp[count])
                    solarAdjustedMRT.append(hourMRT)
                else:
                    ERF.append(0)
                    solarAdjustedMRT.append(radTemp[count])
                    MRTDelta.append(0)
            else:
                    ERF.append(0)
                    solarAdjustedMRT.append(radTemp[count])
                    MRTDelta.append(0)
        return True
    
    
    def parallelMRTCalc():
        def MRTCalc(count):
            if altitudes[count] > 0:
                #Calculate fBes, the fraction of the body that is visible to the sun and is not blocked by the context.
                if len(context) > 0:
                    #First get the sunRays.
                    sunRays = []
                    for point in mannequinMesh:
                        sunRay = rc.Geometry.Ray3d(point, sunVectors[count])
                        sunRays.append(sunRay)
                    
                    #Next check how many of the sunrays are blocked.
                    fBesList = []
                    for ray in sunRays:
                        sunBlocked = False
                        for mesh in context:
                            rayIntersect = rc.Geometry.Intersect.Intersection.MeshRay(mesh, ray)
                            if rayIntersect > 0: sunBlocked = True
                        if sunBlocked == False:fBesList.append(1)
                        else: fBesList.append(0)
                    
                    #Finally, calculate Fbes from that which was blocked.
                    fBes = sum(fBesList)/len(fBesList)
                else:
                    fBes = 1
                
                if fBes > 0.0:
                    #Calculate the diffuse, direct, and global horizontal components of the solar radiation.
                    diffRad = diffSolarRad[HOYS[count]-1]
                    dirNormRad = directSolarRad[HOYS[count]-1]
                    globHorizRad = dirNormRad*(math.sin(altitudes[count])) + diffRad
                    
                    #Define the Azimuth as the SolarCal function understands it.
                    azInit = math.degrees(azimuths[count])
                    #Change the azimuth based on the north angle and the rotation angle of the mannequin.
                    if northAngle != 0.0: azInit = azInit + northAngle
                    if rotationAngle != 0.0: azInit = azInit + rotationAngle
                    
                    #Compute a final Azimuth that can be put through the spline function.
                    azFinal = azInit
                    if azInit > 180:
                        while azFinal > 180:
                            azFinal = azFinal-180
                    elif azInit < 0:
                        while azFinal < 0:
                            azFinal = azFinal+180
                    azFinal = int(azFinal)
                    
                    #Define the Altitude as the SolarCal function understands it.
                    altInit = int(math.degrees(altitudes[count]))
                    if altInit > 90: altFinal = altInit-90
                    else: altFinal = altInit
                    
                    #Calculate the projected area factor from the altitude and azimuth.
                    if bodyPosture_ == 0 or bodyPosture_ == 3:
                        ProjAreaFac = lb_comfortModels.splineStand(azFinal, altFinal)
                    elif bodyPosture_ == 1 or bodyPosture_ == 4 or bodyPosture_ == None:
                        ProjAreaFac = lb_comfortModels.splineSit(azFinal, altFinal)
                    else:
                        ProjAreaFac = lb_comfortModels.splineStand(azFinal, 90-altFinal)
                    
                    # Calculate the ERF of the occupant
                    hourERF = ((0.5*fracEff*skyViewFac*(diffRad + (globHorizRad*groundR))+ (fracEff*ProjAreaFac*fBes*dirNormRad))*winTrans[HOYS[count]-1])*(cloA/0.95)
                    
                    ERF.append(hourERF)
                    #Calculate the MRT delta, the solar adjusted MRT, and the solar adjusted operative temperature.
                    mrtDelt = (hourERF/(fracEff*radTransCoeff))
                    MRTDelta.append(mrtDelt)
                    hourMRT = mrtDelt + (radTemp[count])
                    solarAdjustedMRT.append(hourMRT)
                else:
                    ERF.append(0)
                    solarAdjustedMRT.append(radTemp[count])
                    MRTDelta.append(0)
            else:
                    ERF.append(0)
                    solarAdjustedMRT.append(radTemp[count])
                    MRTDelta.append(0)
            
            hourOrder.append(count)
        
        tasks.Parallel.ForEach(range(len(HOYS)), MRTCalc)
        
        return True
    
    # Compute the radiation for each hour of the year.
    if parallel == False:
        runSuccess = nonParallelMRTCalc()
    else:
        runSuccess = parallelMRTCalc()
    
    #If the process above was run in parallel, re-order the numbers correctly (instead of by when they finished calculating).
    if parallel == True:
        ERF = [x for (y,x) in sorted(zip(hourOrder, ERF))]
        MRTDelta = [x for (y,x) in sorted(zip(hourOrder, MRTDelta))]
        solarAdjustedMRT = [x for (y,x) in sorted(zip(hourOrder, solarAdjustedMRT))]
    
    
    #Add the headers to the computed lists.
    if periodMethod == 0:
        analysisStart = analysisPeriodOrHOY[0]
        analysisEnd = analysisPeriodOrHOY[1]
    else:
        stDate = lb_preparation.hour2Date(analysisPeriodOrHOY)
        analysisStart = stDate
        analysisEnd = stDate
    
    ERF.insert(0,analysisEnd)
    ERF.insert(0,analysisStart)
    ERF.insert(0,'Hourly')
    ERF.insert(0,'kWh/m2')
    ERF.insert(0,'Effective Radiant Field')
    ERF.insert(0,str(location))
    ERF.insert(0,'key:location/dataType/units/frequency/startsAt/endsAt')
    
    MRTDelta.insert(0,analysisEnd)
    MRTDelta.insert(0,analysisStart)
    MRTDelta.insert(0,'Hourly')
    MRTDelta.insert(0,'C')
    MRTDelta.insert(0,'Solar Mean Radiant Temp Delta')
    MRTDelta.insert(0,str(location))
    MRTDelta.insert(0, 'key:location/dataType/units/frequency/startsAt/endsAt')
    
    solarAdjustedMRT.insert(0,analysisEnd)
    solarAdjustedMRT.insert(0,analysisStart)
    solarAdjustedMRT.insert(0,'Hourly')
    solarAdjustedMRT.insert(0,'C')
    solarAdjustedMRT.insert(0,'Solar-Adjusted Mean Radiant Temperature')
    solarAdjustedMRT.insert(0,str(location))
    solarAdjustedMRT.insert(0,'key:location/dataType/units/frequency/startsAt/endsAt')
    
    
    return ERF, MRTDelta, solarAdjustedMRT




#Check the inputs
checkData = False
results = checkTheInputs()

if results!= -1:
    checkData, method, radTemp, mannequinMesh, groundMesh, context, groundR, \
    cloA, winTrans, parallel, analysisPeriodOrHOY, periodMethod, latitude, longitude, timeZone, rotationAngle, northAngle, northVector, epwStr, conversionFac, cumSkyMtx, directSolarRad, diffSolarRad, location, tempOrRad, \
    lb_preparation, lb_visualization, lb_mesh, lb_runStudy_GH, lb_comfortModels,\
    lb_sunpath = results

#Change the inputs or outputs based on what is connected.
checkInputOutput = False
if checkData == True and results!= -1:
    checkInputOutput = manageInputOutput(method)
else: restoreInputOutput()

#Run the analysis.
if _runIt == True and checkData == True and checkInputOutput == True:
    if method == 0 or method == 1:
        effectiveRadiantField, MRTDelta, solarAdjustedMRT, \
        mannequinMesh, legend, legendBasePt, meshFaceResult, meshFaceArea = main(method, radTemp, mannequinMesh, \
        groundMesh, context, groundR, cloA, winTrans, parallel, analysisPeriodOrHOY, periodMethod, latitude, longitude, timeZone, northAngle, \
        northVector, epwStr, conversionFac, cumSkyMtx, location, tempOrRad, lb_preparation, lb_visualization, lb_mesh, \
        lb_runStudy_GH, lb_comfortModels, lb_sunpath)
    else:
        effectiveRadiantField, MRTDelta, solarAdjustedMRT = mainSimple(radTemp, mannequinMesh, context, groundR, cloA, winTrans, analysisPeriodOrHOY, periodMethod, latitude, longitude, timeZone, rotationAngle, northAngle, northVector, epwStr, directSolarRad, diffSolarRad, location, parallel, lb_preparation, lb_comfortModels, lb_sunpath)

#Hide the legend base point.
ghenv.Component.Params.Output[8].Hidden = True