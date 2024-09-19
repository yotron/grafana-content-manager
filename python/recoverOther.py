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
        self.folder = "alerting/" + env
        self.alert_rule_folder = self.folder + "/alert-rules"

    def recoverAlertRules(self):
        print("Recover Alert Rules")
        alertList = glob.glob(self.alert_rule_folder + "/*/*.json")
        for alertFile in alertList:
            print("check alert rule " + alertFile)
            fileAlertRuleJson = funcs.getJsonFromFile(alertFile)
            fileFolderName = fileAlertRuleJson["folderTitle"]
            grafanaFolder = self.graReq.getGrafanaFolderByName(fileFolderName)
            if "title" not in grafanaFolder or grafanaFolder["title"] !=  fileFolderName:
                print("create folder " + fileFolderName)
                self.graReq.createGrafanaFolder(fileFolderName)
                time.sleep(15) # give Grafana a little bit of time to "commit"
                grafanaFolder = self.graReq.getGrafanaFolderByName(fileFolderName)
            grafanaFolderUid = grafanaFolder["uid"]
            manAlertJson = funcs.getJsonFromFile(alertFile)
            manAlertJson["folderUID"] = grafanaFolderUid
            manAlertJson.pop('id', None)
            manAlertJson.pop('uid', None)
            print(self.graReq.createGrafanaAlertFromDict(manAlertJson))

    def recoverContactPoints(self):
        print("Recover Contact Points")
        contactPoints = funcs.getJsonFromFile(self.folder + "/contact-points.json")
        for contactPoint in contactPoints:
            contactPointName = contactPoint["name"]
            if contactPointName != "grafana-default-email" and contactPointName != "email receiver":
                contactPoint.pop('uid', None)
                self.graReq.createContactPointsFromDict(contactPoint)

    def recoverNotificationPolicies(self):
        print("Recover Notification Policies")
        self.graReq.createNotificationPolicy(self.folder + "/notification-policies.json")


    def recoverMuteTimings(self):
        print("Recover Mute Timings")
        muteTimings = funcs.getJsonFromFile(self.folder + "/mute-timings.json")
        for muteTiming in muteTimings:
            self.graReq.createMuteTimingFromDict(muteTiming)

    def recoverTemplates(self):
        print("Recover Templates")
        templates = funcs.getJsonFromFile(self.folder + "/templates.json")
        for template in templates:
            name = template["name"]
            self.graReq.createTemplateFromDict(template, name)