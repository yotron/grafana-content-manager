import os
import glob
from slugify import slugify
from grafanaRequests import grafanaRequests
from grafanaFilesystem import grafanaFilesystem
from funcs import funcs

class syncProcesses:
    def __init__(self, instSetting):
        self.graReq = grafanaRequests(instSetting)
        self.graFS = grafanaFilesystem()
        self.folder = funcs.getDataSourceFolder(instSetting["name"])
        self.DataSource_rule_folder = self.folder + "/DataSource-rules"
        self.commits = []

    def updateGrafanaDataSources(self):
        print("Update Grafana DataSources")
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
        datasources = self.graReq.getGrafanaDataSources()
        for ds in datasources:
            dsjSON = self.graReq.getGrafanaDataSourceByUid(ds["uid"])
            grafanaDataSourceSlug = slugify(dsjSON["name"])
            funcs.writeDictToFile("{0}/{1}.json".format(self.folder, grafanaDataSourceSlug), dsjSON)

    def removeDeletedDataSources(self):
        dataSourceList = glob.glob(self.folder + "/*.json")
        for dataSourceFile in dataSourceList:
            print("check " + dataSourceFile + " for deletion")
            fileSystemDataSourceJson = funcs.getJsonFromFile(dataSourceFile)
            fileSystemDataSourceUid = fileSystemDataSourceJson["uid"]
            grafanaDataSource = self.graReq.getGrafanaDataSourceByUid(fileSystemDataSourceUid)
            if not "uid" in grafanaDataSource:
                print("DataSourceRule " + dataSourceFile + " not available in Grafana. Will delete.")
                self.commits.append("DataSourceRule file " + dataSourceFile + " deleted")
                os.remove(dataSourceFile)