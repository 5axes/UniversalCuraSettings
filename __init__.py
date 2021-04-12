# Copyright (c) 2021 5@xes
# UniversalCuraSettings is released under the terms of the AGPLv3 or higher.

from . import UniversalCuraSettings

def getMetaData():
    return {}

def register(app):
    return {"extension": UniversalCuraSettings.UniversalCuraSettings()}
