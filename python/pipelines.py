import json
import os
from jinja2 import Template

import glob2 as glob
import time

import yaml
from slugify import slugify
from funcs import funcs

class pipelines:
    def __init__(self, git):
        self.git = git

    def createPipelines(self):
        encoding = 'utf-8'
        pipelinePath = "gitlab-pipeline/user-pipelines"
        jinjaPath = "gitlab-pipeline/j2-templates"
        nameSuffix = " created by Grafana Dashboard Security"

        for userPipeline in glob.glob(pipelinePath + "/.*.yml"):
            os.remove(userPipeline)

        for fileName in ["sync-pipelines.yml", "gitlab-update-pipelines.yml"]:
            syncTemplateFile = funcs.readStringFromFile(jinjaPath + "/" + fileName)
            filePath = pipelinePath + "/." + fileName
            funcs.writeStringToFile(filePath, syncTemplateFile)

        setting = funcs.getSetting()
        userTemplateFile = funcs.readStringFromFile(jinjaPath + "/user-pipelines.yml")
        userTemplate = Template(userTemplateFile)
        grafanaInstances = setting["grafanaInstances"]


        for gitPipelineSchedule in self.git.getPipelineSchedules():
            if gitPipelineSchedule["description"].endswith(nameSuffix):
                self.git.deletePipelineSchedule(str(gitPipelineSchedule["id"]))
        for grafanaInstance in grafanaInstances:
            name = grafanaInstance["name"]
            gitName = grafanaInstance["name"] + nameSuffix
            filePath = pipelinePath + "/" + "." + name + ".yml"
            funcs.writeStringToFile(filePath, userTemplate.render(grafanaInstance))
            settingSyncSchedule = grafanaInstance["gitlabSyncSchedule"]
            settingVariables = {}
            if "variables" in settingSyncSchedule:
                settingVariables = settingSyncSchedule["variables"]
            settingVariables["GRAFANA_INSTANCE"] = name
            settingSyncSchedule["description"] = gitName
            newSchedule = self.git.setPipelineSchedule(settingSyncSchedule)
            for key, value in settingVariables.items():
                self.git.setPipelineVariable(str(newSchedule["id"]), key, value)







