# Wind Speed Calculator
# By Chris Mackey, Alex Jacobson and Djordje Spasic
# Chris@MackeyArchitecture.com, Jacobson@gsd.harvard.edu and issworld2000@yahoo.com
# Ladybug started by Mostapha Sadeghipour Roudsari is licensed
# under a Creative Commons Attribution-ShareAlike 3.0 Unported License.

"""
Use this component to calculate wind speed at a specific height for a given terrain type.  By default, the component will calculate ground wind speed, which is useful for comfrt calculations.  Also, by hooking up wind data from an epw file, you can use the resulting data to create a wind rose at any height.

-
Provided by Ladybug 0.0.58
    
    Args:
        north_: Input a vector to be used as a true North direction for the sun path or a number between 0 and 360 that represents the degrees off from the y-axis to make North.  The default North direction is set to the Y-axis (0 degrees).
        _windSpeed_tenMeters: The wind speed from the import EPW component or a number representing the wind speed at 10 meters off the ground in agricultural or airport terrian.  This input also accepts lists of numbers representing different speeds at 10 meters.
        windDirection_: The wind direction from the import EPW component or a number in degrees represeting the wind direction from north,  This input also accepts lists of numbers representing different directions.
        _terrainType: An interger from 0 to 3 that sets the terrain class associated with the output windSpeedAtHeight. Interger values represent the following terrain classes:
            0 = Urban: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        epwTerrain_: An optional interger from 0 to 3 that sets the terrain class associated with the output windSpeedAtHeight. The default is set to 2 for flat clear land, which is typical for most EPW files that are recorded at airports.  Interger values represent the following terrain classes:
            0 = Urban: large city centres, 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = Suburban: suburbs, wooded areas.
            2 = Country: open, with scattered objects generally less than 10m high.
            3 = Water: Flat, unobstructed areas exposed to wind flowing over a large water body (no more than 500m inland).
        heightAboveGround_ : Optional. This is the height above ground for which you would like to measure wind speed. Providing more than one value will generate a list of speeds at each given height. Default height is 1 m above ground, which is what a person standing on the ground would feel.
        analysisPeriod_: If you have connected data from an EPW component, plug in an analysis period from the Ladybug_Analysis Period component to calculate data for just a portion of the year. The default is Jan 1st 00:00 - Dec 31st 24:00, the entire year.
        averageData_: Set to "True" to average all of the wind data that you have connected into a single speed and wind vector. The default is False, which means the component will return a list of all hours within the analysis period.  If se tot Ture, the wind data will be averaged for the entire analysis period into a single value. 
    Returns:
        readMe!: ...
        windSpeedAtHeight: The wind speed at the connected height above the ground.  If averageData_ = True, this will be a single value representing the average speed for all connected values or values within the analysis period at each height. If averageData_ = False, this returns a list of wind speeds for every hour within the analysis period at each height. Note than when averageData_ =  False, the list will include a header specific to each list. This header can be removed by using the "Ladybug_Separate Data" component.
        windVectorAtHeight: Returns a list of vectors representing wind speed and direction at every hour within the analysis period, at each height provided.
"""
ghenv.Component.Name = "Ladybug_Wind Speed Calculator"
ghenv.Component.NickName = 'WindSpeedCalculator'
ghenv.Component.Message = 'VER 0.0.58\nNOV_21_2014'
ghenv.Component.Category = "Ladybug"
ghenv.Component.SubCategory = "1 | AnalyzeWeatherData"
#compatibleLBVersion = VER 0.0.58\nAUG_20_2014
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import Rhino as rc
import scriptcontext as sc
import math
import Grasshopper.Kernel as gh
from Grasshopper import DataTree
from Grasshopper.Kernel.Data import GH_Path
from System import Object


#Make data Tree objects.
windSpeedAtHeight = DataTree[Object]()
windDirectionAtHeight = DataTree[Object]()
windVectorAtHeight = DataTree[Object]()


def checkTheInputs():
    #Define a value that will indicate whether someone has hooked up epw data.
    epwData = False
    epwStr = []
    
    #Check lenth of the _windSpeed_tenMeterslist and evaluate the contents.
    checkData1 = False
    windSpeed = []
    windMultVal = False
    nonPositive = True
    if len(_windSpeed_tenMeters) != 0:
        try:
            if _windSpeed_tenMeters[2] == 'Wind Speed':
                windSpeed = _windSpeed_tenMeters[7:]
                checkData1 = True
                epwData = True
                epwStr = _windSpeed_tenMeters[0:7]
        except: pass
        if checkData1 == False:
            for item in _windSpeed_tenMeters:
                try:
                    if float(item) >= 0:
                        windSpeed.append(float(item))
                        checkData1 = True
                    else: nonPositive = False
                except: checkData1 = False
        if nonPositive == False: checkData1 = False
        if len(windSpeed) > 1: windMultVal = True
        if checkData1 == False:
            warning = '_windSpeed_tenMeters input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData1 = False
        print "Connect wind speed."
    
    #Check lenth of the windDirection_ list and evaluate the contents.
    checkData2 = False
    windDir = []
    dirMultVal = False
    nonPositive = True
    if len(windDirection_) != 0:
        try:
            if windDirection_[2] == 'Wind Direction':
                windDir = windDirection_[7:]
                checkData2 = True
                epwData = True
                epwStr = windDirection_[0:7]
        except: pass
        if checkData2 == False:
            for item in windDirection_:
                try:
                    if float(item) >= 0:
                        windDir.append(float(item))
                        checkData2 = True
                    else: nonPositive = False
                except: checkData2 = False
        if nonPositive == False: checkData2 = False
        if len(windDir) > 1: dirMultVal = True
        if checkData2 == False:
            warning = 'windDirection_ input does not contain valid wind speed in meters per second.  Note that wind speed must be positive.'
            print warning
            ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
    else:
        checkData2 = True
        windDir = [0]
    
    #Define a function to duplicate data
    def duplicateData(data, calcLength):
        dupData = []
        for count in range(calcLength):
            dupData.append(data[0])
        return dupData
    
    #For those lists of length greater than 1, check to make sure that they are all the same length.
    checkData5 = False
    if checkData1 == True and checkData2 == True :
        if windMultVal == True or dirMultVal == True:
            listLenCheck = []
            if windMultVal == True: listLenCheck.append(len(windSpeed))
            if dirMultVal == True: listLenCheck.append(len(windDir))
            
            if all(x == listLenCheck[0] for x in listLenCheck) == True:
                checkData5 = True
                calcLength = listLenCheck[0]
                
                if windMultVal == False: windSpeed = duplicateData(windSpeed, calcLength)
                if dirMultVal == False: windDir = duplicateData(windDir, calcLength)
                
            else:
                calcLength = None
                warning = 'If you have put in lists with multiple values for wind speed or direction, the lengths of these lists must match across the parameters or you have a single value for a given parameter to be applied to all values in the list.'
                print warning
                ghenv.Component.AddRuntimeMessage(gh.GH_RuntimeMessageLevel.Warning, warning)
        else:
            checkData5 = True
            calcLength = 1
    else:
        calcLength = 0
    
    
    #Make the default height at 1 meters if the user has not input a height.
    checkData4 = True
    if heightAboveGround_ == []:
        heightAboveGround = [1]
    else:
        for item in heightAboveGround_:
            if item < 0:
                checkData4 = False
                print "The input heightAboveGround cannot be less than 0."
                w = gh.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(w, "The input heightAboveGround cannot be less than 0.")
            else: pass
        heightAboveGround = heightAboveGround_
    
    #Make the default analyisis period for the whole year if the user has not input one.
    if analysisPeriod_ == []:
        analysisPeriod = [(1, 1, 1), (12, 31, 24)]
    else:
        analysisPeriod = analysisPeriod_
    
    # Evaluate the terrain type to get the right boundary layer thickness and flow exponent.
    checkData3 = True
    if _terrainType != None:
        if _terrainType == 0: print "Terrain set to water."
        elif _terrainType == 1: print "Terrain set to country."
        elif _terrainType == 2: print "Terrain set to suburban."
        elif _terrainType == 3: print "Terrain set to urban."
        else:
            checkData3 = False
            print "Invalid input for _terrainType."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "Invalid input for _terrainType.")
    else:
        print "Connect a value for terrain type."
        checkData3 = False
    
    # Set a defult epwTerrain if none is connected.
    checkData6 = True
    if epwTerrain_ != None:
        if epwTerrain_ <=3 and epwTerrain_ >= 0: epwTerrain = epwTerrain_
        else:
            epwTerrain = None
            checkData6 = False
            print "You have not connected a correct epwTerrain_ type."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "You have not connected a correct epwTerrain_ type.")
    else:
        epwTerrain = 2
        print "epwTerrain_ has been set to 2 for flat clear land, which is typical for most EPW files that are recorded at airports."
    
    #Set the default to not averageData_.
    if averageData_ == None:
        averageData = False
    else:
        averageData = averageData_
    
    if checkData1 == True and checkData2 == True and checkData3 == True and checkData4 == True and checkData5 == True and checkData6 == True:
        checkData = True
    else:
        checkData = False
    
    return checkData, heightAboveGround, analysisPeriod, _terrainType, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr


def main(heightAboveGround, analysisPeriod, terrainType, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr):
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
        lb_wind = sc.sticky["ladybug_WindSpeed"]()
        
        checkData, d, a = lb_wind.readTerrainType(terrainType)
        checkData, metD, metA = lb_wind.readTerrainType(epwTerrain)
        
        if checkData == True:
            #Get the data for the analysis period and strip the header off.
            if epwData == True and analysisPeriod != [(1, 1, 1), (12, 31, 24)]:
                HOYS, months, days = lb_preparation.getHOYsBasedOnPeriod(analysisPeriod, 1)
                hrWindDir = []
                hrWindSpd = []
                for count in HOYS:
                    hrWindSpd.append(windSpeed[count-1])
                    hrWindDir.append(windDir[count-1])
            else:
                hrWindSpd = windSpeed
                hrWindDir = windDir
            
            if averageData == True:
                #Avergage the data.
                avgHrWindSpd = sum(hrWindSpd)/len(hrWindSpd)
                
                avgHrWindDirDeg = sum(hrWindDir)/len(hrWindDir)
                avgHrWindDir = 0.0174532925*avgHrWindDirDeg
                
                #Evaluate each height.
                windSpdHeight = []
                for count, height in enumerate(heightAboveGround):
                    windSpdHeight.append([lb_wind.calcWindSpeedBasedOnHeight(avgHrWindSpd, height, d, a, metD, metA)])
                
                #Declare the wind direction.
                windDirHeight = []
                for count, height in enumerate(heightAboveGround):
                    windDirHeight.append([avgHrWindDirDeg])
                
                #Make wind Vectors.
                windVec = []
                for speed in windSpdHeight:
                    vec = rc.Geometry.Vector3d(0, speed[0], 0)
                    vec.Rotate(avgHrWindDir, rc.Geometry.Vector3d.ZAxis)
                    windVec.append([vec])
                
                #If there is a north angle hooked up, rotate the vectors.
                if north_ != None:
                    northAngle, northVector = lb_preparation.angle2north(north_)
                    for vec in windVec:
                        vec[0].Rotate(northAngle, rc.Geometry.Vector3d.ZAxis)
                else: pass
                
            else:
                #Add the headers to the wind speed data trees.
                if epwData == True:
                    for count, height in enumerate(heightAboveGround):
                        windSpeedAtHeight.Add(epwStr[0], GH_Path(count))
                        windSpeedAtHeight.Add(epwStr[1], GH_Path(count))
                        windSpeedAtHeight.Add('Wind Speed', GH_Path(count))
                        windSpeedAtHeight.Add('m/s', GH_Path(count))
                        windSpeedAtHeight.Add(epwStr[4], GH_Path(count))
                        windDirectionAtHeight.Add(epwStr[0], GH_Path(count))
                        windDirectionAtHeight.Add(epwStr[1], GH_Path(count))
                        windDirectionAtHeight.Add('Wind Direction', GH_Path(count))
                        windDirectionAtHeight.Add('degrees', GH_Path(count))
                        windDirectionAtHeight.Add(epwStr[4], GH_Path(count))
                        if analysisPeriod != [(1, 1, 1), (12, 31, 24)]:
                            windSpeedAtHeight.Add(analysisPeriod[0], GH_Path(count))
                            windSpeedAtHeight.Add(analysisPeriod[1], GH_Path(count))
                            windDirectionAtHeight.Add(analysisPeriod[0], GH_Path(count))
                            windDirectionAtHeight.Add(analysisPeriod[1], GH_Path(count))
                        else:
                            windSpeedAtHeight.Add(epwStr[5], GH_Path(count))
                            windSpeedAtHeight.Add(epwStr[6], GH_Path(count))
                            windDirectionAtHeight.Add(epwStr[5], GH_Path(count))
                            windDirectionAtHeight.Add(epwStr[6], GH_Path(count))
                
                #Evaluate each height.
                windSpdHeight = []
                for height in heightAboveGround:
                    initWindSpd = []
                    for speed in hrWindSpd:
                        initWindSpd.append(lb_wind.calcWindSpeedBasedOnHeight(speed, height, d, a, metD, metA))
                    windSpdHeight.append(initWindSpd)
                
                #Declare the wind direction.
                windDirHeight = []
                for height in heightAboveGround:
                   windDirHeight.append(hrWindDir)
                
                #Make the wind vectors.
                windVec = []
                for list in windSpdHeight:
                    initWindVec = []
                    for count, speed in enumerate(list):
                        vec = rc.Geometry.Vector3d(0, speed, 0)
                        vec.Rotate(hrWindDir[count]*0.0174532925, rc.Geometry.Vector3d.ZAxis)
                        initWindVec.append(vec)
                    windVec.append(initWindVec)
                
                #If there is a north angle hooked up, rotate the vectors.
                if north_ != None:
                    northAngle, northVector = lb_preparation.angle2north(north_)
                    for list in windVec:
                        for vec in list:
                            vec.Rotate(northAngle, rc.Geometry.Vector3d.ZAxis)
                else: pass
            
            return windSpdHeight, windVec, windDirHeight
        else:
            print "You have not connected a correct Terrain type."
            w = gh.GH_RuntimeMessageLevel.Warning
            ghenv.Component.AddRuntimeMessage(w, "You have not connected a correct Terrain type.")
            return [], [], []
    else:
        print "You should first let the Ladybug fly..."
        w = gh.GH_RuntimeMessageLevel.Warning
        ghenv.Component.AddRuntimeMessage(w, "You should first let the Ladybug fly...")
        return [], [], []



#Check the inputs.
checkData, heightAboveGround, analysisPeriod, terrainType, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr = checkTheInputs()

#Run the function.
if checkData == True:
    res = main(heightAboveGround, analysisPeriod, terrainType, epwTerrain, averageData, windSpeed, windDir, epwData, epwStr)
    
    if res!=-1:
        windSpdAtHght, windVecAtHght, windDirHeight = res
        
        #Unpack the lists of lists in Python.
        for count, list in enumerate(windSpdAtHght):
            for item in list:
                windSpeedAtHeight.Add(item, GH_Path(count))
        
        for count, list in enumerate(windVecAtHght):
            for item in list:
                windVectorAtHeight.Add(item, GH_Path(count))
        
        for count, list in enumerate(windDirHeight):
            for item in list:
                windDirectionAtHeight.Add(item, GH_Path(count))
