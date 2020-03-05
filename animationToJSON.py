#Animation data to json script
import maya.cmds as cmds
import json
import os




#takes a file path (with inteded directory at the end)
def createDirectory(_filePath, *kwargs):
    if not os.path.exists(_filePath):
        os.mkdir(_filePath)


#Self explanitory but feed corresponding text field as an arguement to populate
def fileSelection( _targetTextField, *args):
    global plainTextFileLocation
    selectedFileName = cmds.fileDialog2(fileMode=0, caption="Define file name and location")
    #print(selectedFileName)
    plainTextFileLocation = selectedFileName[0].encode('ascii','ignore')
    cmds.textField( _targetTextField, edit=True, tx=(plainTextFileLocation))


def getSceneName(*kwargs):
     filePath = cmds.file(q=True, sn=True)
     fileName = os.path.basename(filePath)
     sceneName, ext = os.path.splitext(fileName)
     return sceneName


'''
#A function to return the name of the parent curve to the curve given
def getParentCurve(_curveName, *kwargs):
    cmds.select(cl=True)
'''     


#function to check if an attibute Exists on an object. takes the arguements object and attribute
#returns True or False
def attrExistenceCheck(_object, _attribute,*kwargs):
    fullAttrName = ((str(_object))+ '.' +(str(_attribute)))
    #print("Checking for ", fullAttrName)
    checker = cmds.objExists(fullAttrName)
    return checker


#Takes a target as the arguement and returns a list of the common 
#attributes on the object that are visible in the channnel box
def getChannelBoxAttrs(_target):
    cmds.select(cl=True)
    cmds.select(_target)
    longAttrs = (cmds.listAnimatable())
    shortAttrs = []
    
    for x in longAttrs:
        #print(x)
        temp = str(x)
        #print(temp)
        temp = (temp.split("|"))
        temp = str(temp[-1])
        temp = temp.split(".")
        temp = temp[-1]
        #print(temp)
        shortAttrs.append(temp)
    
    
    return shortAttrs


#queries the scenes curves and gets the top level transforms, puts them into a list
#and returns them
def getSceneCurves(*kwargs):
    curveShapes = cmds.ls(type='nurbsCurve')
    curves = []
    #print(curveShapes)
    
    for c in curveShapes:
        curveTopLevel = cmds.listRelatives(c, p=1, type = 'transform')
        curveName = (curveTopLevel[0])
        curveName = curveName.encode('ascii','ignore')
        #print(curveName)
        curves.append(curveName)
        
    return curves



#queries keyFrames on a curve for its channel values
#returns a dictionary of the atrributes and their values at each keyed frame
def GetKeyedAttrVals(_queryTarget, _queryKeysList, *kargs):
    target = _queryTarget
    keyedFrames = _queryKeysList
    
    attrChannels = getChannelBoxAttrs(target)
    
    animDataDictionary = {}
    attrData = {}
    if keyedFrames != None:
        for k in keyedFrames:
            curFrame = int(k)
            cmds.currentTime(curFrame)
            attrData = {}
            
            for a in attrChannels:
                tempAttrName = (_queryTarget + '.' + a)
                atData = cmds.getAttr(tempAttrName)
                attrData[a] = atData
            
            animDataDictionary[k] = attrData
        
        return animDataDictionary
    return




        
#queries a curve for which frames it has keyframes on
#returns a list with that data
def GetCurveKeyIndexs(_queryTarget, *kwargs):
    try:
        tempList = cmds.keyframe(_queryTarget, q=True)
        #print(tempList)
        tempSet = set(tempList)
        kFrames = list(tempSet)
        kFrames.sort()
        return(kFrames)
        
    except:
        print("ERROR: During the get curve key index function")
        print("No Leads as to why. Good luck bug hunting")


# takes a dictionary and a destination file path to.. create a json file with the dictionary data
def animDictionaryToJson(_dictionary, _outputLocation, *kwargs):
    with open(_outputLocation, 'wb') as output:
        json.dump(_dictionary, output, indent = 4)
        return 'Built, now inspect the output'
    



#main data extraction function for quering the curves in a scene and running the other
#functions and storing their returned data in a format to send to the Json file making function
def getDataFromScene(_outputDir, *kwargs):
    sceneCurves = getSceneCurves()
    
    animKFrames = {}
    animKFrameData = {}
    
    
    for i in sceneCurves:
        #temp list to get the frames that are keyframed on the current curve
        tempFrameData = GetCurveKeyIndexs(i)
        #print(i)
        #print(tempFrameData)
        
        #building the output dictionaries
        animKFrames[i] = tempFrameData
        animKFrameData[i] = GetKeyedAttrVals(i, tempFrameData)
        
    
    outputDirectory = _outputDir
    outputFolder = getSceneName()
    
    #create the output folder
    outputFolderPath = (outputDirectory + "\\" + outputFolder)
    createDirectory(outputFolderPath)
    
    
    #storing the intended file name and paths as strings
    framesWFile = (outputFolderPath + "\\" +"AnimFrames.json")
    dataWFile = (outputFolderPath + "\\" +"AnimData.json")
    
    #write the anim Frames json file
    animDictionaryToJson(animKFrames, framesWFile)
    
    #write the anim Data json file
    animDictionaryToJson(animKFrameData, dataWFile)
    
    
#self explanitory but it loads the Json file data to a dictionary so that
#it might be applied to the curves in a file... #this is mostly to be used to load the data onto rigs
#in the next function.
def loadJsonDataIntoDict(_jsonFilePath):
    with open(_jsonFilePath) as jsonFile:
        data = json.load(jsonFile)
        return data


#the main load data onto rig function. This being called will take an animation Directory that 
#has the two json files created in the other functions. It'll use the Data from the two Json files
#and key the data onto the current rig file's curves
def loadAnimDataOntoRig(_directoryPath, *kwargs):
    #animFrames = {} #looks like this was reduntant information
    animData = {}
    
    path = _directoryPath
    
    #animFrames = loadJsonDataIntoDict(path + '\\AnimFrames.json')
    animData = loadJsonDataIntoDict(path + '\\AnimData.json')
    
    #print(animFrames)
    #print(animData)
    for item, value in animData.items():
        #currently item is referring to the ctl curve in the dict
        #print(item)
        if cmds.objExists(item):
            cmds.select(cl=True)
            cmds.select(item)
            print(item)
        
            #currently value is referring to the dictionary that has frames as items and a dictionary of...
            #... Attributes and values as its key:value pairs
            #print(value)
            try:
                for key, val in value.items():
                    #currently the key is refering to frame value
                    #print(key)
                    cmds.currentTime(int(float(key)))
                    #currently the Val is the Dictionary of attributes and values
                    #print(val)
                    
                    
                    
                    for k, v in val.items():
                        #currently this far down the loop k is equal to the attribute name
                        #print(k)
                        
                        #currently this far down the loop v is equal to the attribute value
                        #print(v)
                        
                        attrName = k
                        attrExistence = attrExistenceCheck(item, k)
                        
                        if attrExistence == True:
                            fullN = (str(item) + '.' + str(k))
                            cmds.setAttr(fullN, v)
                            cmds.setKeyframe()
                        else:
                            print("kicked out of the loop at item :" + item + " and attr " + attrName )
                            continue
                            
                        
            except:
                continue                
        else:
            print("kicked out of the loop at item :" + item )
            continue             
    
    




loadAnimDataOntoRig('C:\\Users\\bstep\\Desktop\\Mech09_victory')

#loadAnimDataOntoRig('C:\\Users\\bstep\\Desktop\\Mech09_V')


#getDataFromScene('C:\\Users\\bstep\\Desktop\\Mech09_Victory')

