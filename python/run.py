import os
import sys

from syncDb import syncProcesses as syncDbClass
from cleanGrafana import deleteProcesses as delClass
from recoverDb import recoverProcesses as recDbClass
from recoverAlerting import recoverProcesses as recAlertingClass
from recoverOther import recoverProcesses as recOtherClass
from syncOther import syncProcesses as syncOtherClass
from syncAlerting import syncProcesses as syncAlertClass
from syncDb import syncProcesses as syncDbClass
from gitlabRequests import gitlabRequests as gitlabRequestsClass
from funcs import funcs
from pipelines import pipelines as pipelinesClass


def sync():
    commitMsgList = []
    for instSetting in funcs.getSetting()["grafana"]:
        syncOther = syncOtherClass(instSetting)
        syncOther.updateGrafanaDataSources()
        syncOther.removeDeletedDataSources()
        syncDb = syncDbClass(instSetting)
        syncDb.updateGrafanaDashboards()
        syncDb.removeDeletedDashboards()
        syncAlert = syncAlertClass(instSetting)
        syncAlert.updateGrafanaAlertRules()
        syncAlert.removeDeletedAlertRules()
        syncAlert.updateGrafanaUnifiedAlerts()
        allCommits = syncDb.commits + syncAlert.commits
        if allCommits.__len__() > 0:
           commitMsgList.append("Instance {0}: {1}".format(instSetting["name"], str.join(', ', allCommits)))
    overAllCommitMsg = str.join(',', commitMsgList)
    gitlab = gitlabRequestsClass()
    gitlab.gitCommit(overAllCommitMsg)

def cleanDataSources():
    startEnvVar = os.getenv("DATASOURCES")
    if startEnvVar != "cleanup":
        print("Will not start cleanUp process. Start variable not set properly")
        sys.exit(1)
    delDs = delClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    delDs.cleanDataSources()

def recoverDataSources():
    recOther = recOtherClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    recOther.recoverDataSources()

def cleanDashboards():
    startEnvVar = os.getenv("DASHBOARDS")
    if startEnvVar != "cleanup":
        print("Will not start cleanUp process. Start variable not set properly")
        sys.exit(1)
    delDb = delClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    delDb.cleanDashboards()
    delDb.cleanDashboardsFolder()

def recoverDashboards():
    instanceSetting = funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE"))
    recDb = recDbClass(instanceSetting, instanceSetting)
    recDb.recoverDashboards()

def cleanUnifiedAlerting():
    startEnvVar = os.getenv("ALERTING")
    if startEnvVar != "cleanup":
        print("Will not start cleanUp process. Start variable not set properly")
        sys.exit(1)
    delDb = delClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    delDb.cleanAlertRules()
    delDb.cleanOther()
    delDb.cleanAlertsFolder()

def recoverUnifiedAlerting():
    recAlerting = recAlertingClass(funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE")))
    recAlerting.recoverContactPoints()
    recAlerting.recoverAlertRules()
    recAlerting.recoverNotificationPolicies()
    recAlerting.recoverMuteTimings()
    recAlerting.recoverTemplates()

def updatePipelines():
    gitlab = gitlabRequestsClass()
    pipelines = pipelinesClass(gitlab)
    pipelines.createPipelines()
    gitlab.getPipelineSchedules()
    gitlab.gitCommit("GitLab Pipelines Update")

def updateGrafanaInstance():
    target = os.getenv("GRAFANA_INSTANCE")
    source = os.getenv("GRAFANA_SOURCE_INSTANCE")
    if os.getenv("UPDATE") != os.getenv("CI_JOB_NAME"):
        print("Will not run update process. Start variable not set properly.")
        sys.exit(1)
    print("Start updating {0} from {1}".format(target, source))
    delDb = delClass(funcs.getInstanceSetting(target))
    delDb.cleanDashboards()
    delDb.cleanDashboardsFolder()
    srcInstanceSetting = funcs.getInstanceSetting(source)
    trgInstanceSetting = funcs.getInstanceSetting(target)
    recDb = recDbClass(srcInstanceSetting, trgInstanceSetting)
    recDb.recoverDashboards()

if __name__ == "__main__":
    args = sys.argv
    try:
        globals()[args[1]](*args[2:])
    except Exception as excep:
        funcs.handleException(excep)
