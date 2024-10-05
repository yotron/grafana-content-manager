import os
from jinja2 import Template

import glob2 as glob

from funcs import funcs

class pipelines:
    def __init__(self, git):
        self.git = git
        self.setting = funcs.getSetting()

    def createPipelines(self):
        pipelinePath = "gitlab-pipeline/user-pipelines"
        jinjaPath = "gitlab-pipeline/j2-templates"
        syncScheduleDescription = "syncSchedule created by Grafana Dashboard Manager"

        for userPipeline in glob.glob(pipelinePath + "/.*.yml"):
            os.remove(userPipeline)

        for gitPipelineSchedule in self.git.getPipelineSchedules():
            if gitPipelineSchedule["description"] == syncScheduleDescription:
                self.git.deletePipelineSchedule(str(gitPipelineSchedule["id"]))

        schedule = self.setting["gitlab"]["schedule"]
        schedule["description"] = syncScheduleDescription
        self.git.setPipelineSchedule(schedule)

        userTemplateFile = funcs.readStringFromFile("{0}/{1}".format(jinjaPath, "user-pipelines.yml"))
        userTemplate = Template(userTemplateFile)
        updateTemplateFile = funcs.readStringFromFile("{0}/{1}".format(jinjaPath, "update-pipelines.yml"))
        updateTemplate = Template(updateTemplateFile)
        grafanaInstances = self.setting["grafana"]
        for grafanaInstance in grafanaInstances:
            name = grafanaInstance["name"]
            filePath = "{0}/{1}.yml".format(pipelinePath, name)
            funcs.writeStringToFile(filePath, userTemplate.render(grafanaInstance))
            if "allowRecoveryTo" in grafanaInstance:
                for recTo in grafanaInstance["allowRecoveryTo"]:
                    names ={"source": name, "target": recTo}
                    filePath = "{0}/{1}-{2}.yml".format(pipelinePath, name, recTo)
                    funcs.writeStringToFile(filePath, updateTemplate.render(names))








