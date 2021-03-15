# Copyright (c) 2020 5@xes
# ImportExportProfiles is released under the terms of the AGPLv3 or higher.

from . import ImportExportProfiles

def getMetaData():
    return {}

def register(app):
    return {"extension": ImportExportProfiles.ImportExportProfiles()}
