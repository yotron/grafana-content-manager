from funcs import funcs

class grafanaFilesystem:
  def getFilesystemDashboardMetadata(self, filePath):
    json = funcs.getJsonFromFile(filePath)
    if json is None:
      return {
        "uid": None,
        "folder": None,
        "version": None,
        "slug": None
      }
    return {
      "uid": json["dashboard"]["uid"],
      "folder": json["meta"]["folderTitle"],
      "version": json["meta"]["version"],
      "slug": json["meta"]["slug"]
    }

  def getFilesystemAlertMetadata(self, filePath):
    json = funcs.getJsonFromFile(filePath)
    if json is None:
      return {}
    return {
      "uid": json["uid"],
      "updated": json["updated"],
      "title": json["title"]
    }

