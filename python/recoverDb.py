import os
import sys

import glob2 as glob
import time

from grafanaRequests import grafanaRequests
from grafanaFilesystem import grafanaFilesystem
from funcs import funcs

class recoverProcesses:
    def __init__(self, sourceInstSetting, targetInstSetting):
        self.graReq = grafanaRequests(targetInstSetting)
        self.sourceFolder = funcs.getDashboardFolder(sourceInstSetting["name"])
        self.dataSourceFolder = funcs.getDataSourceFolder(sourceInstSetting["name"])
        self.mappings = funcs.dataSourceUidsMappings(self.graReq, self.dataSourceFolder)


    def recoverDashboards(self):
        amountDB = self.graReq.getGrafanaDashboardsAmount()
        if amountDB > 0:
            print("Cannot recover Dashboards. {0} Dashboard(s) available.".format(str(amountDB)))
            sys.exit(1)
        folderList = glob.glob(self.sourceFolder + "/*/")
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
            for dashboardFile in glob.glob(folderSlug + "/*.json"):
                if os.path.isfile(dashboardFile):
                    print("check file " + dashboardFile)
                    manDashboardJson = funcs.getJsonFromFile(dashboardFile)["dashboard"]
                    manDashboardJson.pop('id', None)
                    manDashboardJson.pop('uid', None)
                    grafanaFolderUid = grafanaFolder["uid"]
                    manDashboardJson = self.changeUids(manDashboardJson, self.mappings)
                    dashboardTmpJson = {
                        "dashboard": manDashboardJson,
                        "folderUid": grafanaFolderUid,
                        "overwrite": False,
                        "message": "commit by CICD"
                    }
                    print(self.graReq.createGrafanaDashboard(dashboardTmpJson))


    def changeUids(self, dict, uidMappings):
        for panelNr, panel in enumerate(dict["panels"]):
            if "datasource" in panel and "uid" in panel["datasource"]:
                sourceDsUid = panel["datasource"]["uid"]
                dict["panels"][panelNr]["datasource"]["uid"] = uidMappings[sourceDsUid]
            if "targets" in panel:
                for targetNr, target in enumerate(panel["targets"]):
                    if "datasource" in target and "uid" in target["datasource"]:
                        sourceDsUid = target["datasource"]["uid"]
                        dict["panels"][panelNr]["targets"][targetNr]["datasource"]["uid"] = uidMappings[sourceDsUid]
        for templatingListEntryNr, templatingListEntry in enumerate(dict["templating"]["list"]):
            if "datasource" in templatingListEntry:
                if "uid" in templatingListEntry["datasource"]:
                    sourceDsUid = templatingListEntry["datasource"]["uid"]
                    dict["templating"]["list"][templatingListEntryNr]["datasource"]["uid"]= uidMappings[sourceDsUid]
                elif isinstance(templatingListEntry["datasource"], str):
                    sourceDsUid = templatingListEntry["datasource"]
                    dict["templating"]["list"][templatingListEntryNr]["datasource"] = uidMappings[sourceDsUid]
        return dict