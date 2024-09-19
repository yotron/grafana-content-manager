import sys

import requests
import os
import json

class grafanaRequests:
  def __init__(self):
    self.baseUrl = os.environ['GRAFANA_URL']
    self.apiKey = os.environ['GRAFANA_APIKEY']
    self.baseHeader = {
      "Authorization": "Bearer " + self.apiKey,
      "Content-Type": "application/json"
    }
    self.verify = True

  def handleRequest(selfs, r):
    if r.status_code >= 400:
      print("Could not request Grafana dashboards, Request failed, StatusCode: " + str(r.status_code))
      sys.exit(4)
    return r.json()

  def getGrafanaFolder(self) -> list:
    r = requests.get(self.baseUrl + "/api/folders/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getGrafanaFolderByName(self, name):
    jsonDict = self.getGrafanaFolder()
    return self.filterItemInDict(jsonDict, "title", name)

  def getGrafanaFolderByUuid(self, uuid):
    r = requests.get(self.baseUrl + "/api/folders/" + uuid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def createGrafanaFolder(self, folderName):
    json={"title": folderName}
    r = requests.post(self.baseUrl + "/api/folders/", json = json, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def createGrafanaDashboard(self, dict):
    r = requests.post(self.baseUrl + "/api/dashboards/db", json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def createGrafanaDashboardFromFile(self, filePath):
    f=open(filePath,'rb')
    r = requests.post(self.baseUrl + "/api/dashboards/db", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
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
    return self.handleRequest(r)

  def listGrafanaDashboards(self):
    r = requests.get(self.baseUrl + "/api/search/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getGrafanaDashboardsAmount(self):
    dbs = self.listGrafanaDashboards()
    return self.filterItemsInDict(dbs, "type", "dash-db").__len__()

  def getGrafanaDashboard(self, uuid):
    r = requests.get(self.baseUrl + "/api/dashboards/uid/" + uuid, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getAlerts(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/alert-rules/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

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

  def createTemplateFromDict(self, dict, uuid):
    r = requests.put(self.baseUrl + "/api/v1/provisioning/templates/" + uuid, json=dict, headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def getMuteTimings(self) -> list:
    r = requests.get(self.baseUrl + "/api/v1/provisioning/policies/", headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getMuteTimingsAmount(self):
    return self.getMuteTimings().__len__()

  def createMuteTimingFromFile(self, filePath):
    f=open(filePath,'rb')
    r = requests.put(self.baseUrl + "/api/v1/provisioning/mute-timings/", data=f.read(), headers=self.headerXDisProv(), verify=self.verify)
    return self.handleRequest(r)

  def createMuteTimingFromDict(self, dict):
    r = requests.put(self.baseUrl + "/api/v1/provisioning/mute-timings/", json=dict, headers=self.headerXDisProv(), verify=self.verify)
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

  def getGrafanaDashboardResponse(self, uuid) -> requests.Response:
    r = requests.get(self.baseUrl + "/api/dashboards/uid/" + uuid, headers=self.baseHeader, verify=self.verify)
    return r

  def getGrafanaDashboardsMetadata(self):
    dbs = self.listGrafanaDashboards()
    result = [{"uid": d["uid"], "folder": d["folderTitle"]} for d in dbs if d["type"] == "dash-db" and "folderTitle" in d]
    return result

  def getGrafanaDashboardMetadata(self, uuid):
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

  def filterItemsInDict(self, dict, key, value):
    result = [d for d in dict if d[key] == value]
    return result

  def filterItemInDict(self, dict, key, value):
    result = self.filterItemsInDict(dict, key, value)
    if result.__len__() == 1:
      return result[0]
    return {}

  def headerXDisProv(self):
    newheader = self.baseHeader
    newheader["X-Disable-Provenance"] = ''
    return newheader