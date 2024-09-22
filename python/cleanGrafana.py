from grafanaRequests import grafanaRequests
from grafanaFilesystem import grafanaFilesystem

class deleteProcesses:
    def __init__(self, instSetting):
        self.graReq = grafanaRequests(instSetting)
        self.graFS = grafanaFilesystem()
        self.commits = []
        self.folder = "dashboards/" + instSetting["name"]

    def cleanDashboards(self):
        print("Delete all Grafana Dashboards")

        dbMetadata = self.graReq.getGrafanaDashboardsMetadata()
        for grafanaDbMetadataListEntry in dbMetadata:
            grafanaDbUid = grafanaDbMetadataListEntry['uid']
            grafanaDbJson = self.graReq.getGrafanaDashboard(grafanaDbUid)
            folderTitle = grafanaDbJson["meta"]["folderTitle"]
            dbName = grafanaDbJson["dashboard"]["title"]
            self.graReq.deleteGrafanaDashboard(grafanaDbUid)
            print("Dashboard {0} in folder {1} deleted".format(dbName, folderTitle))

    def cleanFolder(self):
        print("Delete all Folder")
        folderMetadata = self.graReq.getGrafanaFolderMetadata()
        for folderMetadataListEntry in folderMetadata:
            grafanaFolderUid = folderMetadataListEntry['uid']
            grafanaFolderName = folderMetadataListEntry['title']
            self.graReq.deleteGrafanaFolder(grafanaFolderUid)
            print("Folder {0} deleted".format(grafanaFolderName))

    def cleanDashboardsFolder(self):
        print("Delete all Folder of Dashboards")
        folderMetadata = self.graReq.getGrafanaFolderMetadata()
        unifiedAlertFolderUids = self.graReq.getAlertsFolders()
        for folderMetadataListEntry in folderMetadata:
            grafanaFolderUid = folderMetadataListEntry['uid']
            grafanaFolderName = folderMetadataListEntry['title']
            if grafanaFolderUid in unifiedAlertFolderUids:
                print("Folder {0} not deleted. Contains an Alert.".format(grafanaFolderName))
            else:
                self.graReq.deleteGrafanaFolder(grafanaFolderUid)
                print("Folder {0} deleted".format(grafanaFolderName))

    def cleanAlertsFolder(self):
        print("Delete all Folder of Unified Alerts")
        folderMetadata = self.graReq.getGrafanaFolderMetadata()
        dashboardFolderUids = self.graReq.getGrafanaDashboardsFolderUids()
        for folderMetadataListEntry in folderMetadata:
            grafanaFolderUid = folderMetadataListEntry['uid']
            grafanaFolderName = folderMetadataListEntry['title']
            if grafanaFolderUid in dashboardFolderUids:
                print("Folder {0} not deleted. Contains a Dashboard.".format(grafanaFolderName))
            else:
                self.graReq.deleteGrafanaFolder(grafanaFolderUid)
                print("Folder {0} deleted".format(grafanaFolderName))

    def cleanAlertRules(self):
        print("Delete all Grafana AlertRules")

        alerts = self.graReq.getAlerts()
        for alert in alerts:
            alertUid = alert['uid']
            alertTitle = alert['title']
            folderUid = alert['folderUID']
            folder = self.graReq.getGrafanaFolderByUuid(folderUid)
            folderTitle = folder["title"]
            self.graReq.deleteGrafanaAlert(alertUid)
            print("AlertRule {0} in folder {1} deleted".format(alertTitle, folderTitle))


    def cleanOther(self):
        print("Delete all other configs")

        self.graReq.deleteNotificationPolicies()
        print("{0} deleted".format("Notification policy"))

        muteTimings = self.graReq.getMuteTimings()
        for muteTiming in muteTimings:
            muteTimingName = muteTiming['name']
            self.graReq.deleteMuteTiming(muteTimingName)
            print("MuteTiming {0} deleted".format(muteTimingName))

        contactPoints = self.graReq.getContactPoints()
        for contactPoint in contactPoints:
            contactPointName = contactPoint['name']
            if contactPointName != "email receiver":
                contactPointUid = contactPoint['uid']
                self.graReq.deleteContactPoint(contactPointUid)
                print("Contact Points {0} deleted".format(contactPointName))

        templates = self.graReq.getTemplates()
        for template in templates:
            templateName = template['name']
            self.graReq.deleteTemplate(templateName)
            print("Template {0} deleted".format(templateName))

