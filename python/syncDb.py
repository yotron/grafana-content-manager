import os
import glob2 as glob
import sys

from slugify import slugify
from grafanaRequests import grafanaRequests
from grafanaFilesystem import grafanaFilesystem
from funcs import funcs

class syncProcesses:
    def __init__(self, instSetting):
        self.graReq = grafanaRequests(instSetting)
        self.graFS = grafanaFilesystem()
        self.commits = []
        self.folder = "dashboards/" + instSetting["name"]

    def updateGrafanaDashboards(self):
        print("Update Grafana Dashboards")
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)

        dbMetadata = self.graReq.getGrafanaDashboardsMetadata()

        for grafanaDbMetadataListEntry in dbMetadata:
            grafanaDbUid = grafanaDbMetadataListEntry['uid']
            grafanaDbJson = self.graReq.getGrafanaDashboard(grafanaDbUid)
            grafanaDbMetadata = self.graReq.getGrafanaDashboardMetadata(grafanaDbUid)
            grafanaDbFolderSlug = slugify(grafanaDbMetadata["folder"])
            grafanaDbVersion = grafanaDbMetadata["version"]
            grafanaDbSlug = grafanaDbMetadata["slug"]
            if not os.path.exists(self.folder + "/" + grafanaDbFolderSlug):
              print("creating new folder in Git: dashboards/" + grafanaDbFolderSlug)
              os.makedirs(self.folder + "/" + grafanaDbFolderSlug)
            objName = grafanaDbFolderSlug + "/" +  grafanaDbSlug + ".json"
            objPath = self.folder + "/" + objName
            fileSystemDbJson = self.graFS.getFilesystemDashboardMetadata(objPath)
            fileSystemDbVersion = fileSystemDbJson["version"]
            fileSystemDbUid = fileSystemDbJson["uid"]
            if fileSystemDbVersion == None:
              print("Add new dashboard file: " + objName)
              self.commits.append("dashboard " + objName + " created")
              funcs.writeDictToFile( objPath, grafanaDbJson)
            elif fileSystemDbUid != grafanaDbUid:
                print("Update dashboard file: " + objName + " to UID " + str(grafanaDbUid))
                self.commits.append("dashboard " + objName + " updated to UID " + str(grafanaDbVersion))
                funcs.writeDictToFile(objPath, grafanaDbJson)
            elif fileSystemDbVersion != grafanaDbVersion:
              print("Update dashboard file: " + objName + " to version " + str(grafanaDbVersion))
              self.commits.append("dashboard " + objName + " updated to version " + str(grafanaDbVersion))
              funcs.writeDictToFile(objPath, grafanaDbJson)
            else:
              print("No update needed for dashboard file: " + objName)

    def removeDeletedDashboards(self):
        dbList = glob.glob(self.folder + "/*/*.json")
        for dbFile in dbList:
            print("check " + dbFile + " for deletion")
            fileSystemDbJson = self.graFS.getFilesystemDashboardMetadata(dbFile)
            fileSystemDbUid = fileSystemDbJson["uid"]
            fileSystemDbFolder = fileSystemDbJson["folder"]
            fileSystemDbSlug = fileSystemDbJson["slug"]
            grafanaDbResponse = self.graReq.getGrafanaDashboardResponse(fileSystemDbUid)
            if grafanaDbResponse.status_code == 404:
                print("Dashboard " + dbFile + " not available in Grafana. Will delete.")
                self.commits.append("dashboard " + dbFile + " deleted")
                os.remove(dbFile)
            elif grafanaDbResponse.status_code == 200:
                json = grafanaDbResponse.json()
                grafanaDbFolder = json["meta"]["folderTitle"]
                if grafanaDbFolder != fileSystemDbFolder:
                    print("Dashboard " + dbFile + " was moved to other folder of Grafana. Will delete.")
                    self.commits.append("dashboard " + dbFile + " deleted")
                    os.remove(dbFile)
            else:
                print("Error when  get dashboard json from Grafana, StatusCode: " + str(grafanaDbResponse.status_code))
                print("Error when  get dashboard json from Grafana, Message: " + str(grafanaDbResponse.text))
                sys.exit(4)
            if glob.glob(os.path.dirname(dbFile) + "/*.json").__len__() == 0:
                os.rmdir(os.path.dirname(dbFile))