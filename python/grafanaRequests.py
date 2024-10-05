import sys

import requests
import os
from funcs import funcs

class grafanaRequests:
  def __init__(self, instSetting):
    self.baseUrl = instSetting["apiUrl"]
    self.apiKey = os.getenv(instSetting["apiKeyEnvVariable"])
    self.baseHeader = {
      "Authorization": "Bearer " + self.apiKey,
      "Content-Type": "application/json"
    }
    self.verify = True

  def handleRequest(self, r):
    if r.status_code >= 400:
      print("Request failed, StatusCode: {0}, text: {1}".format(str(r.status_code), r.text))
      sys.exit(4)
    return r.json()

  def handleRequestNoReturn(self, r):
    if r.status_code >= 400:
      print("Could not request Grafana dashboards, Request failed, StatusCode: " + str(r.status_code))
      sys.exit(4)
    return

  def getGrafanaFolder(self) -> list:
    r = requests.get(self.baseUrl + "/api/folders/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getGrafanaFolderByName(self, name) -> dict:
    jsonDict = self.getGrafanaFolder()
    return funcs.filterItemInDict(jsonDict, "title", name)

  def getGrafanaFolderByUuid(self, uuid) -> dict:
    r = requests.get(self.baseUrl + "/api/folders/" + uuid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def createGrafanaFolder(self, folderName):
    json={"title": folderName}
    r = requests.post(self.baseUrl + "/api/folders/", json = json, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def deleteGrafanaFolder(self, uid):
    r = requests.delete(self.baseUrl + "/api/folders/" + uid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def createGrafanaDashboard(self, dict):
    r = requests.post(self.baseUrl + "/api/dashboards/db", json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def createGrafanaDashboardFromFile(self, filePath):
    f=open(filePath,'rb')
    r = requests.post(self.baseUrl + "/api/dashboards/db", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def deleteGrafanaDashboard(self, uuid):
    r = requests.delete(self.baseUrl + "/api/dashboards/uid/" + uuid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def listGrafanaDashboards(self):
    r = requests.get(self.baseUrl + "/api/search/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getGrafanaDashboardsAmount(self):
    dbs = self.listGrafanaDashboards()
    return funcs.filterItemsInDict(dbs, "type", "dash-db").__len__()

  def getGrafanaDashboard(self, uuid):
    r = requests.get(self.baseUrl + "/api/dashboards/uid/" + uuid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def createGrafanaAlertFromFile(self, filePath):
    f=open(filePath,'rb')
    r = requests.post(self.baseUrl + "/api/v1/provisioning/alert-rules", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    print("Response " + r.raw + " StatusCode: " + str(r.status_code))

    if r.status_code != "200":
      print("Could not create Grafana alert-rule, Request failed, StatusCode: " + str(r.status_code))

  def createGrafanaAlertFromDict(self, dict):
    r = requests.post(self.baseUrl + "/api/v1/provisioning/alert-rules", json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def deleteGrafanaAlert(self, uuid):
    r = requests.delete(self.baseUrl + "/api/v1/provisioning/alert-rules/" + uuid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def getAlerts(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/alert-rules/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getAlertsFolders(self):
    alerts = self.getAlerts()
    folderUids = [d['folderUID'] for d in alerts if 'folderUID' in d]
    return folderUids

  def getGrafanaAlertsAmount(self):
    return self.getAlerts().__len__()

  def getAlertByUuid(self, uuid):
    r = requests.get(self.baseUrl + "/api/v1/provisioning/alert-rules/" + uuid, headers=self.baseHeader, verify=self.verify)
    if r.status_code == 200:
      return r.json()
    elif r.status_code == 404 and r.raw == "":
      return {}
    else:
       print("Failed to get Grafana Alert, Request failed, StatusCode: $statusCode, message: $body")
    return ""

  def getNotificationPolicies(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/policies/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def deleteNotificationPolicies(self):
    r = requests.delete(self.baseUrl + "/api/v1/provisioning/policies/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def getNotificationPoliciesAmount(self):
    return self.getNotificationPolicies().__len__()

  def createNotificationPolicy(self, filePath):
    f=open(filePath,'rb')
    r = requests.put(self.baseUrl + "/api/v1/provisioning/policies/", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def getTemplates(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/templates/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getTemplatesAmount(self):
    return self.getTemplates().__len__()

  def createTemplateFromFile(self, filePath, uuid):
    f=open(filePath,'rb')
    r = requests.put(self.baseUrl + "/api/v1/provisioning/templates/" + uuid, data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def createTemplateFromDict(self, dict, name):
    r = requests.put(self.baseUrl + "/api/v1/provisioning/templates/" + name, json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def deleteTemplate(self, name):
    r = requests.delete(self.baseUrl + "/api/v1/provisioning/templates/" + name, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def getMuteTimings(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/mute-timings/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def deleteMuteTiming(self, name):
    r = requests.delete(self.baseUrl + "/api/v1/provisioning/mute-timings/" + name, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def getMuteTimingsAmount(self):
    return self.getMuteTimings().__len__()

  def createMuteTimingFromFile(self, filePath):
    f=open(filePath,'rb')
    r = requests.put(self.baseUrl + "/api/v1/provisioning/mute-timings/", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def createMuteTimingFromDict(self, dict):
    r = requests.post(self.baseUrl + "/api/v1/provisioning/mute-timings/", json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def getContactPoints(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/contact-points/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getContactPointsAmount(self):
    return self.getContactPoints().__len__()

  def createContactPointsFromFile(self, filePath):
    f=open(filePath,'rb')
    r = requests.post(self.baseUrl + "/api/v1/provisioning/contact-points/", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def createContactPointsFromDict(self, dict):
    r = requests.post(self.baseUrl + "/api/v1/provisioning/contact-points/", json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def deleteContactPoint(self, uid):
    r = requests.delete(self.baseUrl + "/api/v1/provisioning/contact-points/" + uid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def getGrafanaDashboardResponse(self, uuid) -> requests.Response:
    r = requests.get(self.baseUrl + "/api/dashboards/uid/" + uuid, headers=self.baseHeader, verify=self.verify)
    return r

  def getGrafanaDashboardsMetadata(self) -> list:
    dbs = self.listGrafanaDashboards()
    result = [{"uid": d["uid"], "folder": d["folderTitle"]} for d in dbs if d["type"] == "dash-db" and "folderTitle" in d]
    return result

  def getGrafanaDashboardsFolderUids(self) -> list:
    dbs = self.listGrafanaDashboards()
    folderUids = [d["folderUid"] for d in dbs if d["type"] == "dash-db" and "folderTitle" in d]
    return folderUids

  def getGrafanaDashboardMetadata(self, uuid) -> dict:
    db= self.getGrafanaDashboard(uuid)
    return {
      "uid": db["dashboard"]["uid"],
      "folder": db["meta"]["folderTitle"],
      "version": db["meta"]["version"],
      "slug": db["meta"]["slug"]
    }

  def getGrafanaDashboardMetadataWithStatus(self, uuid):
    grafanaDbResp=self.getGrafanaDashboardResponse(uuid)
    if grafanaDbResp.status_code == 404:
      return {
        "uid": "",
        "folder": "",
        "version": "",
        "slug": "",
        "statusCode": grafanaDbResp.status_code
      }
    if grafanaDbResp.status_code == 200:
      json = grafanaDbResp.json()
      return {
        "uid": json["dashboard"]["uid"],
        "folder": json["meta"]["folderTitle"],
        "version": json["dashboard"]["version"],
        "slug": json["meta"]["slug"],
        "statusCode": grafanaDbResp.status_code
      }
    print("Could not request Grafana Metadata, Request failed, Response: " + grafanaDbResp.raw)
    return None

  def getGrafanaFolderMetadata(self) -> dict:
    dbs = self.listGrafanaDashboards()
    result = [{"uid": d["uid"], "title": d["title"]} for d in dbs if d["type"] == "dash-folder"]
    return result

  def getGrafanaDataSources(self) -> dict:
    r = requests.get(self.baseUrl + "/api/datasources", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getGrafanaDataSourcesMetadata(self) -> list:
    ds = self.getGrafanaDataSources()
    result = [{"uid": d["uid"], "name": d["name"]} for d in ds]
    return result

  def getGrafanaDataSourceByUid(self, uid) -> dict:
    r = requests.get(self.baseUrl + "/api/datasources/uid/" + uid, headers=self.baseHeader, verify=self.verify)
    if r.status_code == 200:
      return r.json()
    elif r.status_code == 404:
      return {}
    else:
      print("Failed to get Grafana DatSource, Request failed, StatusCode: $statusCode, message: $body")
    return None

  def createDataSourceDashboard(self, dict):
    r = requests.post(self.baseUrl + "/api/datasources", json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def deleteGrafanaDataSourceByUid(self, uid):
    r = requests.delete(self.baseUrl + "/api/datasources/uid/" + uid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestNoReturn(r)

  def getGrafanaDataSourceAmount(self):
    return self.getGrafanaDataSources().__len__()

  def headerXDisProv(self):
    newheader = self.baseHeader
    newheader["X-Disable-Provenance"] = ''
    return newheader