import glob
import json
import os
import pathlib
import sys
import traceback

import yaml

class funcs:
    @staticmethod
    def getAlertingFolder(instName):
        return "content/" + instName + "/alerting"

    @staticmethod
    def getDashboardFolder(instName):
        return "content/" + instName + "/dashboards"

    @staticmethod
    def getDataSourceFolder(instName):
        return "content/" + instName + "/datasources"

    @staticmethod
    def handleException(excep):
        print("Error " + str(type(excep)) + " occured.")
        print(excep.args)     # arguments stored in .args
        print(excep)
        print(traceback.format_exc())
        sys.exit(4)

    @staticmethod
    def readStringFromFile(filePath):
        if os.path.isfile(filePath):
            f=open(filePath,'rb')
            return f.read().decode("utf-8")
        return None

    @staticmethod
    def getJsonFromFile(filePath):
        if os.path.isfile(filePath):
            f=open(filePath,'rb')
            return json.loads(f.read())
        return None

    @staticmethod
    def writeDictToFile(filePath, dict):
        f = open(filePath,'w')
        jsonDict = json.dumps(dict, indent=2)
        f.write(str(jsonDict))
        f.close()
        return

    @staticmethod
    def writeStringToFile(filePath, string):
        f = open(filePath,'w')
        f.write(string)
        f.close()
        return

    @staticmethod
    def appendStringToFile(filePath, string):
        f = open(filePath,'a')
        f.write(string)
        f.close()
        return

    @staticmethod
    def writeBytesToFile(filePath, bytes):
        f = open(filePath,'wb')
        f.write(bytes)
        f.close()
        return

    @staticmethod
    def getSetting():
        f=open("setting.yml",'rb')
        setting = yaml.safe_load(f)
        f.close()
        return setting

    @staticmethod
    def getInstanceSetting(grafana_instance):
        settings = funcs.getSetting()
        for setting in settings["grafana"]:
            if setting["name"] == grafana_instance:
              return setting

    @staticmethod
    def getGitlabSetting():
        settings = funcs.getSetting()
        return settings["gitlab"]

    @staticmethod
    def filterItemsInDict(dict, key, value):
        result = [d for d in dict if d[key] == value]
        return result

    @staticmethod
    def filterItemInDict(dict, key, value):
        result = funcs.filterItemsInDict(dict, key, value)
        if result.__len__() == 1:
            return result[0]
        return {}

    @staticmethod
    def dataSourceUidsMappings(graReq, dataSourceFolder):
        targetDSJson = graReq.getGrafanaDataSourcesMetadata()
        mappings = {}

        for sourceDsFile in glob.glob(dataSourceFolder + "/*.json"):
            sourceDs = funcs.getJsonFromFile(sourceDsFile)
            sourceDsName = sourceDs["name"]
            sourceDsUid = sourceDs["uid"]
            dsTargetNames = funcs.filterItemsInDict(targetDSJson, "name", sourceDsName)
            if dsTargetNames.__len__() != 1:
                print("No unique datasource in target Grafana found for datasoure '{0}'".format(sourceDsName))
                sys.exit(1)
            mappings[sourceDsUid] = dsTargetNames[0]["uid"]
        return mappings

