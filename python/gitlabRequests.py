import sys
import traceback
from wsgiref.util import request_uri
from urllib.parse import urlparse, urlunparse
import requests
import os
import urllib.request
import urllib.parse
from git import Repo, GitCommandError
from funcs import funcs

class gitlabRequests:
  def __init__(self):
    # Environment variabels
    self.baseUrl = os.environ['GRAFANA_URL']
    self.gitLabUrl = os.environ['CI_API_V4_URL'] # https://gitlab.apps.k8s.local/api/v4
    self.projectUrl = os.environ['CI_REPOSITORY_URL'] # https://gitlab-ci-token:[MASKED]@gitlab.apps.k8s.local/yotron/grafana-backup.git
    self.projectId = str(os.environ['CI_PROJECT_ID']) # 2
    self.repositoryUrl = os.environ['CI_PROJECT_URL'] # https://gitlab.apps.k8s.local/yotron/grafana-backup

    self.baseHeader = {
      "PRIVATE-TOKEN": os.environ['GITLAB_JOB_TOKEN'],
      "Content-Type": "application/json"
    }

    setting = funcs.getSetting()
    self.branch = setting["gitlab"]["branch"]
    self.repo = Repo(".")
    self.repo.git.checkout(self.branch)
    self.params = {"ref": self.branch}
    self.repo.config_writer().set_value("user", "name", os.environ['CI_JOB_NAME']).release()
    self.repo.config_writer().set_value("user", "email", os.environ['GITLAB_USER_EMAIL']).release()
    parsed = urlparse(os.environ['CI_REPOSITORY_URL'])
    domain = parsed.netloc.split("@")[-1]
    domain = f"{os.environ['CI_JOB_NAME']}:{os.environ['GITLAB_JOB_TOKEN']}@{domain}"
    unparsed = (parsed[0], domain, parsed[2], parsed[3], parsed[4], parsed[5])
    self.repo.remotes['origin'].set_url(urlunparse(unparsed))
    self.verify = True


  def getPipelineSchedules(self):
    r = requests.get(self.gitLabUrl + "/projects/" + self.projectId + "/pipeline_schedules", params=self.params, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def getPipelineSchedule(self, scheduleId):
    r = requests.get(self.gitLabUrl + "/projects/" + self.projectId + "/pipeline_schedules/" + scheduleId, params=self.params, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def setPipelineSchedule(self, dict):
      r = requests.post(self.gitLabUrl + "/projects/" + self.projectId + "/pipeline_schedules/", params=self.params, json=dict, headers=self.baseHeader, verify=self.verify)
      return self.handleRequest(r)

  def deletePipelineSchedule(self, pipelineScheduleId):
    r = requests.delete(self.gitLabUrl + "/projects/" + self.projectId + "/pipeline_schedules/" + pipelineScheduleId, params=self.params, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestRaw(r)

  def setPipelineVariable(self, scheduleId, key, value):
    varDict={}
    varDict["key"] = key
    varDict["value"] = value
    r = requests.post(self.gitLabUrl + "/projects/" + self.projectId + "/pipeline_schedules/" + scheduleId + "/variables", params=self.params, json=varDict, headers=self.baseHeader, verify=self.verify)
    return self.handleRequest(r)

  def deletePipelineVariable(self, scheduleId, key):
    r = requests.delete(self.gitLabUrl + "/projects/" + self.projectId + "/pipeline_schedules/" + scheduleId + "/variables/" + key, params=self.params, headers=self.baseHeader, verify=self.verify)
    return self.handleRequestRaw(r)

  def gitCommit(self, msg):
      self.repo.git.add(all=True)
      try:
        self.repo.git.commit('-m', msg)
        self.repo.remotes.origin.push(refspec=self.branch)
      except GitCommandError as gitError:
        print(traceback.format_exc())
      except Exception as e:
        print(traceback.format_exc())

  def handleRequest(self, r):
    if r.status_code >= 400:
      print("Could not request " + r.url + " against GIT, Request failed, StatusCode: " + str(r.status_code))
      print("Error: " + str(r.text))
      sys.exit(4)
    return r.json()

  def handleRequestRaw(self, r):
    if r.status_code >= 400:
      print("Could not request " + r.url + " against GIT, Request failed, StatusCode: " + str(r.status_code))
      print("Error: " + str(r.text))
      sys.exit(4)
    return r