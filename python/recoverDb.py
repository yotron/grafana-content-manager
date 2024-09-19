import json
import os
import glob2 as glob
import time

from slugify import slugify
from grafanaRequests import grafanaRequests
from grafanaFilesystem import grafanaFilesystem
from funcs import funcs

class recoverProcesses:
    def __init__(self, env):
        self.graReq = grafanaRequests()
        self.graFS = grafanaFilesystem()
        self.folder = "dashboards/" + env

    def recoverDashboards(self):
        folderList = glob.glob(self.folder + "/*/")
        if folderList.__len__() == 0:
            print("Nothing to recover found!")
        for folderSlug in folderList:
            print("check folder " + folderSlug)
            files = glob.glob(folderSlug + "*.json")
            if files.__len__() == 0:
                print("Empty Folder! Shall not happen.")
            jsonFile = funcs.getJsonFromFile(files[0])
            fileFolderName = jsonFile["meta"]["folderTitle"]
            grafanaFolder = self.graReq.getGrafanaFolderByName(fileFolderName)
            grafanaFolderName = ""
            if "title" in grafanaFolder: grafanaFolderName = grafanaFolder["title"]
            if grafanaFolderName != fileFolderName:
                print("create folder " + fileFolderName)
                self.graReq.createGrafanaFolder(fileFolderName)
                time.sleep(15) # give Grafana a little bit of time to "commit"
                grafanaFolder = self.graReq.getGrafanaFolderByName(fileFolderName)
            grafanaFolderUid = grafanaFolder["uid"]
            for dashboardFile in glob.glob(folderSlug + "/*.json"):
                if os.path.isfile(dashboardFile):
                    print("check file " + dashboardFile)
                    manDashboardJson = funcs.getJsonFromFile(dashboardFile)["dashboard"]
                    manDashboardJson.pop('id', None)
                    manDashboardJson.pop('uid', None)
                    dashboardTmpJson = {
                        "dashboard": manDashboardJson,
                        "folderUid": grafanaFolderUid,
                        "overwrite": False,
                        "message": "commit by CICD"
                    }
                    print(self.graReq.createGrafanaDashboard(dashboardTmpJson))








