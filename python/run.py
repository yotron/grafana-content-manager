import os
import sys
import traceback

from syncDb import syncProcesses as syncDbClass
from recoverDb import recoverProcesses as recDbClass
from recoverOther import recoverProcesses as recOtherClass
from syncOther import syncProcesses as syncOtherClass
from gitlabRequests import gitlabRequests as gitlabRequestsClass
from funcs import funcs
from pipelines import pipelines as pipelinesClass

def prepare():
    instSetting = funcs.getInstanceSetting(os.getenv("GRAFANA_INSTANCE"))
    os.environ["GRAFANA_URL"] = instSetting["apiUrl"]
    os.environ["GRAFANA_APIKEY"] = os.environ[instSetting["apiKeyEnvVariable"]]

def syncDashboards():
    prepare()
    syncDb = syncDbClass(os.getenv("GRAFANA_INSTANCE"))
    syncDb.updateGrafanaDashboards()
    syncDb.removeDeletedDashboards()
    funcs.createCommitMsgEnvVar(syncDb.commits)
    print("commitMsg: " + os.environ['COMMIT_MSG' ])

def recoverDashboards():
    prepare()
    recDb = recDbClass(os.getenv("GRAFANA_INSTANCE"))
    recDb.recoverDashboards()

def syncOther():
    prepare()
    syncOther = syncOtherClass(os.getenv("GRAFANA_INSTANCE"))
    syncOther.updateGrafanaAlertRules()
    syncOther.removeDeletedAlertRules()
    syncOther.updateGrafanaUnifiedAlerts()
    funcs.createCommitMsgEnvVar(syncOther.commits)
    print("commitMsg: " + os.environ['COMMIT_MSG' ])

def recoverOther():
    prepare()
    recOther = recOtherClass(os.getenv("GRAFANA_INSTANCE"))
    recOther.recoverAlertRules()
    recOther.recoverContactPoints()
    recOther.recoverNotificationPolicies()
    recOther.recoverMuteTimings()
    recOther.recoverTemplates()

def updatePipelines():
    gitlab = gitlabRequestsClass()
    pipelines = pipelinesClass(gitlab)
    pipelines.createPipelines()
    gitlab.getPipelineSchedules()
    gitlab.gitCommit()

def commitChanges():
    gitlab = gitlabRequestsClass()
    gitlab.gitCommit()

if __name__ == "__main__":
    args = sys.argv
    try:
        globals()[args[1]](*args[2:])
    except Exception as excep:
        funcs.handleException(excep)
