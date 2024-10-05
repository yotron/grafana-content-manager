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
        self.folder = funcs.getAlertingFolder(instSetting["name"])
        self.alert_rule_folder = self.folder + "/alert-rules"
        self.commits = []

    def updateGrafanaAlertRules(self):
        print("Update Grafana UnifiedAlerting AlertRules")
        if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
        if not os.path.isdir(self.alert_rule_folder):
            os.makedirs(self.alert_rule_folder)
        alerts = self.graReq.getAlerts()
        for grafanaAlertListEntry in alerts:
            grafanaAlertUid = grafanaAlertListEntry["uid"]
            grafanaAlertUpdated = grafanaAlertListEntry["updated"]
            grafanaAlertTitle = grafanaAlertListEntry["title"]
            grafanaAlertFolderUuid = grafanaAlertListEntry["folderUID"]
            grafanaAlertFolder = self.graReq.getGrafanaFolderByUuid(grafanaAlertFolderUuid)["title"]
            grafanaAlertFolderName = slugify(grafanaAlertFolder)
            grafanaAlertJson = self.graReq.getAlertByUuid(grafanaAlertUid)
            grafanaAlertJson["folderTitle"] = grafanaAlertFolder
            grafanaAlertSlug = slugify(grafanaAlertTitle)
            objName = grafanaAlertFolderName + "/" +  grafanaAlertSlug + ".json"
            print("check alert: " + objName + " with uid " + grafanaAlertUid + " and update " + grafanaAlertUpdated)
            folderPath = self.alert_rule_folder + "/" + grafanaAlertFolderName
            if not os.path.isdir(folderPath):
                print("creating new folder: " + folderPath)
                os.makedirs(folderPath)
            path = self.alert_rule_folder + "/" + objName
            fileSystemAlertJson = self.graFS.getFilesystemAlertMetadata(path)
            if "updated" in fileSystemAlertJson:
                fileSystemAlertUpdated = fileSystemAlertJson["updated"]
                if fileSystemAlertUpdated != grafanaAlertUpdated:
                    print("Update AlertRule file: " + path)
                    self.commits.append("AlertRule " + path + " updated.")
                    funcs.writeDictToFile(path, grafanaAlertJson)
                else:
                    print("No update needed for AlertRule file: " + path)
            else:
                print("Create new AlertRule file: " + path)
                self.commits.append("AlertRule " + path + " created.")
                funcs.writeDictToFile(path, grafanaAlertJson)

    def removeDeletedAlertRules(self):
        if os.path.isdir(self.alert_rule_folder):
            alertList = glob.glob(self.alert_rule_folder + "/*/*.json")
            for alertFile in alertList:
               print("check " + alertFile + " for deletion")
               fileSystemAlertJson = funcs.getJsonFromFile(alertFile)
               fileSystemAlertUid = fileSystemAlertJson["uid"]
               fileSystemAlertUpdated = fileSystemAlertJson["updated"]
               grafanaAlert = self.graReq.getAlertByUuid(fileSystemAlertUid)
               if "updated" in grafanaAlert:
                   grafanaAlertUpdated = grafanaAlert["updated"]
                   if grafanaAlertUpdated != fileSystemAlertUpdated:
                       print("AlertRule " + alertFile + " not available in Grafana. Will delete.")
                       self.commits.append("AlertRule file " + alertFile + " deleted")
                       os.remove(alertFile)
               else:
                   print("AlertRule " + alertFile + " not available in Grafana. Will delete.")
                   self.commits.append("AlertRule file " + alertFile + " deleted")
                   os.remove(alertFile)

    def updateGrafanaUnifiedAlerts(self):
        print("Update Grafana UnifiedAlerting Others")
        notPol = self.graReq.getNotificationPolicies()
        funcs.writeDictToFile(self.folder + "/notification-policies.json", notPol)

        muteTimings = self.graReq.getMuteTimings()
        funcs.writeDictToFile(self.folder + "/mute-timings.json", muteTimings)

        conPointsPol = self.graReq.getContactPoints()
        funcs.writeDictToFile(self.folder + "/contact-points.json", conPointsPol)

        templates = self.graReq.getTemplates()
        templates = sorted(templates, key=lambda d: d['name'])
        funcs.writeDictToFile(self.folder + "/templates.json", templates)
        self.commits.append("Unified Alerting syncronised")
