import os
import sys

from syncDb import syncProcesses as syncDbClass
from recoverDb import recoverProcesses as recDbClass
from cleanGrafana import deleteProcesses as delDbClass
from recoverOther import recoverProcesses as recOtherClass
from syncOther import syncProcesses as syncOtherClass
from gitlabRequests import gitlabRequests as gitlabRequestsClass
from funcs import funcs
from pipelines import pipelines as pipelinesClass

def sync():
    commitMsgList = []
    for instSetting in funcs.getSetting()["grafana"]:
        syncDb = syncDbClass(instSetting)
        syncDb.updateGrafanaDashboards()
        syncDb.removeDeletedDashboards()
        syncOther = syncOtherClass(instSetting)
        syncOther.updateGrafanaAlertRules()
        syncOther.removeDeletedAlertRules()
        syncOther.updateGrafanaUnifiedAlerts()
        allCommits = syncDb.commits + syncOther.commits
        if allCommits.__len__() > 0:
           commitMsgList.append("Instance {0}: {1}".format(instSetting["name"], str.join(', ', allCommits)))
    overAllCommitMsg = str.join(',', commitMsgList)
    gitlab = gitlabRequestsClass()
    gitlab.gitCommit(overAllCommitMsg)

def recoverDashboards():
    recDb = recDbClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    recDb.recoverDashboards()

def recoverOther():
    recOther = recOtherClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    recOther.recoverAlertRules()
    recOther.recoverContactPoints()
    recOther.recoverNotificationPolicies()
    recOther.recoverMuteTimings()
    recOther.recoverTemplates()

def cleanDashboards():
    startEnvVar = os.getenv("DASHBOARDS")
    if startEnvVar != "cleanup":
        print("Will not start cleanUp process. Start variable not set properly")
        sys.exit(0)
    delDb = delDbClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    delDb.cleanDashboards()
    delDb.cleanDashboardsFolder()

def cleanUnifiedAlerting():
    startEnvVar = os.getenv("ALERTING")
    if startEnvVar != "cleanup":
        print("Will not start cleanUp process. Start variable not set properly")
        sys.exit(0)
    delDb = delDbClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    delDb.cleanAlertRules()
    delDb.cleanOther()
    delDb.cleanAlertsFolder()

def updatePipelines():
    gitlab = gitlabRequestsClass()
    pipelines = pipelinesClass(gitlab)
    pipelines.createPipelines()
    gitlab.getPipelineSchedules()
    gitlab.gitCommit("GitLab Pipelines Update")

if __name__ == "__main__":
    args = sys.argv
    try:
        globals()[args[1]](*args[2:])
    except Exception as excep:
        funcs.handleException(excep)
