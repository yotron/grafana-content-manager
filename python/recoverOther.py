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
        self.folder = "alerting/" + instSetting["name"]
        self.alert_rule_folder = self.folder + "/alert-rules"

    def recoverAlertRules(self):
        print("Recover Alert Rules")
        amountAlerts = self.graReq.getGrafanaAlertsAmount()
        if amountAlerts > 0:
            print("Cannot recover AlertRules. {0} AlertRule(s) available.".format(str(amountAlerts)))
            sys.exit(1)
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
            template["version"] = None
            self.graReq.createTemplateFromDict(template, name)