import sys

import glob2 as glob
import time

from grafanaRequests import grafanaRequests
from grafanaFilesystem import grafanaFilesystem
from funcs import funcs

class recoverProcesses:
    def __init__(self, instSetting):
        self.graReq = grafanaRequests(instSetting)
        self.graFS = grafanaFilesystem()
        self.folder = funcs.getDataSourceFolder(instSetting["name"])

    def recoverDataSources(self):
        print("Recover DataSources")
        amountDataSources = self.graReq.getGrafanaDataSourceAmount()
        if amountDataSources > 0:
            print("Cannot recover DataSources. {0} DataSource(s) available.".format(str(amountDataSources)))
            sys.exit(1)
        dataSourceList = glob.glob(self.folder + "/*.json")
        for dataSourceFile in dataSourceList:
            print("check dataSource rule " + dataSourceFile)
            fileDataSourceJson = funcs.getJsonFromFile(dataSourceFile)
            fileDataSourceJson.pop('id', None)
            fileDataSourceJson.pop('uid', None)
            print(self.graReq.createDataSourceDashboard(fileDataSourceJson))