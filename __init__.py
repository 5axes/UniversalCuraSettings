# Copyright (c) 2021 5@xes
# JonasUniversalCuraSettings is released under the terms of the AGPLv3 or higher.

from . import JonasUniversalCuraSettings

def getMetaData():
    return {}

def register(app):
    return {"extension": JonasUniversalCuraSettings.JonasUniversalCuraSettings()}
