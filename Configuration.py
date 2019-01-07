import json, subprocess, os, copy,shutil, platform, pygame, Common
from ast import literal_eval as make_tuple
from pprint import pprint

configuration = None
theme = json.load(open('theme/theme.json'))
listeners = []
types = ["RS97", "RS07", "K3P"]

def getConfiguration():   
    if(configuration == None):      
        reloadConfiguration()

    return configuration

def reloadConfiguration(): 
    global configuration
    configuration = json.load(open('config/config.json'))
    if("version" not in configuration):
        configuration["version"] = "0"

    if("type" not in configuration["options"] or configuration["options"]["type"] not in types):
        print("forcing type to RS97")
        configuration["options"]["type"] = "RS97"

    configuration["mainMenu"] = []
  
    setResolution()


    if( configuration["options"]["configName"] != "main" and 
        not os.path.exists(os.path.dirname("config/" + configuration["options"]["configName"]  + "/"))):
         changeConfigName("main")
         reloadConfiguration()
         return

    if os.path.exists(os.path.dirname("config/" + configuration["options"]["configName"]  + "/")):
        fileList = os.listdir("config/" + configuration["options"]["configName"]  + "/")
        Common.quick_sort(fileList)       
        for name in fileList:
            try:         
                if(os.path.isdir("config/" + configuration["options"]["configName"]  + "/" + name )):       
                    entry = json.load(open("config/" + configuration["options"]["configName"]  + "/" + name + "/config.json"))
                    entry["source"] = name
                    configuration["mainMenu"].append(entry)
                    if(entry["type"] == "native"):
                        entry["data"] = []
                        try:
                            itemlist =  os.listdir("config/" + configuration["options"]["configName"]  + "/" + name + "/items")
                            Common.quick_sort(itemlist) 
                            for itemName in itemlist:
                                item = json.load(open("config/" + configuration["options"]["configName"]  + "/" + name + "/items/" + itemName))
                                item["source"] = itemName
                                entry["data"].append(item)
                        except Exception as ex:
                            print(str(ex))
                

            except Exception as ex:
                print(str(ex))                  
    

def setResolution():
    global configuration
   
    if(isRS97()):
        configuration["screenWidth"] = 320
        configuration["screenHeight"] = 240
    
    #RS07 & K3P
    else:
        configuration["screenWidth"] = 480
        configuration["screenHeight"] = 272
    
    #windows platform or mac
    if(platform.processor() != ""):
        configuration["screenWidth"] = 320
        configuration["screenHeight"] = 240

def changeConfigName(name):
    allConfig = copy.deepcopy(configuration)
    allConfig["options"]["configName"] = name
    del allConfig["mainMenu"]

    with open('config/config.json', 'w') as fp: 
        json.dump(allConfig, fp,sort_keys=True, indent=4)

def saveConfiguration():

    try:
        subprocess.Popen(["sync"])
    except Exception:
        pass
      
    try:
        shutil.rmtree("config/" + configuration["options"]["configName"]) 
    except Exception as ex:
        print(str(ex))     
    
    allConfig = copy.deepcopy(configuration)
    main = allConfig["mainMenu"]
    allConfig.pop('mainMenu', None)

    with open('config/config.json', 'w') as fp: 
        json.dump(allConfig, fp,sort_keys=True, indent=4)

    for index, item in enumerate(main):
        if( "source" not in item):
            fileName = "config/" + configuration["options"]["configName"]  + "/" + str(index).zfill(3) + " " +  item["name"] + "/config.json" 
        else:
            fileName = "config/" + configuration["options"]["configName"]  + "/" + item["source"] + "/config.json"

        if(item["type"] == "native"):
            data = item["data"]
            item.pop('data', None)
            for dataIndex, dataItem in enumerate(data):
                if("source" not in dataItem):
                    dataName = "config/" + configuration["options"]["configName"]  + "/" + str(index).zfill(3) + " " +  item["name"] + "/items/" + str(dataIndex).zfill(3) + " " + dataItem["name"] + ".json"
                else:
                    dataName = "config/" + configuration["options"]["configName"]  + "/" + item["source"] + "/items/" + dataItem["source"]

                if "source" in dataItem: del dataItem["source"]
                storeConfigPart(dataName, dataItem)

        if(item["type"] != "lastPlayed"):
            if "source" in item: del item["source"]
            storeConfigPart(fileName, item)
        elif(item["type"] == "lastPlayed"):
            dataName = "config/" + configuration["options"]["configName"] + "/lastPlayed.json"
            del item["data"]
            storeConfigPart(dataName, item)

       
    for l in listeners:
        l()
       


def storeConfigPart(fileName, item):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(fileName, 'w') as fp: 
        json.dump(item, fp,sort_keys=True, indent=4)

        

def getTheme():
    return theme

def toColor(input):
    return make_tuple(input)

def isRS97():
    return "type" in configuration["options"] and configuration["options"]["type"] == "RS97"

def addConfigChangedCallback(listener):
    listeners.append(listener)


def getPathData(path, data = None):
    if(data == None):
        data = configuration

    if path and data:
        args = path.split("/")
        element  = args[0]
        if element:
            newPath = '/'.join(args[1:])
            value = data.get(element)
            return value if len(args) == 1 else getPathData(value, newPath)

