import os
from jinja2 import Template

import glob2 as glob

from funcs import funcs

class pipelines:
    def __init__(self, git):
        self.git = git

    def createPipelines(self):
        pipelinePath = "gitlab-pipeline/user-pipelines"
        jinjaPath = "gitlab-pipeline/j2-templates"
        syncScheduleDescription = "syncSchedule created by Grafana Dashboard Manager"

        for userPipeline in glob.glob(pipelinePath + "/.*.yml"):
            os.remove(userPipeline)

        setting = funcs.getSetting()
        userTemplateFile = funcs.readStringFromFile(jinjaPath + "/user-pipelines.yml")
        userTemplate = Template(userTemplateFile)
        grafanaInstances = setting["grafana"]

        for gitPipelineSchedule in self.git.getPipelineSchedules():
            if gitPipelineSchedule["description"] == syncScheduleDescription:
                self.git.deletePipelineSchedule(str(gitPipelineSchedule["id"]))

        schedule = setting["gitlab"]["schedule"]
        schedule["description"] = syncScheduleDescription
        self.git.setPipelineSchedule(schedule)

        for grafanaInstance in grafanaInstances:
            name = grafanaInstance["name"]
            filePath = pipelinePath + "/" + "." + name + ".yml"
            funcs.writeStringToFile(filePath, userTemplate.render(grafanaInstance))








