import glob
import json
import os
import pathlib
import sys
import traceback

import yaml

class funcs:
    @staticmethod
    def handleException(excep):
        print("Error " + str(type(excep)) + " occured.")
        print(excep.args)     # arguments stored in .args
        print(excep)
        print(traceback.format_exc())
        sys.exit(4)

    @staticmethod
    def readStringFromFile(filePath):
        print(pathlib.Path(filePath).parent.absolute())
        if os.path.isfile(filePath):
            f=open(filePath,'rb')
            return f.read().decode("utf-8")
        return None

    @staticmethod
    def getJsonFromFile(filePath):
        print(pathlib.Path(filePath).parent.absolute())
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

