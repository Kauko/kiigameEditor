# -*- coding: UTF-8 -*-
import json


DEFAULT_FALLBACK = "Text missing"
DEFAULT_TRANSLATION = "loc_eng.json"


def loadTranslation(translation=DEFAULT_TRANSLATION):
    # This apparently does not make this variable "truly global"
    # It just tells python to not to make a new "loc" variable
    # inside this function, but rather use the one already defined
    # in this module
    global loc
    loc = json.loads(open(translation).read())
    return loc


def translate(parent, translation, fallback=DEFAULT_FALLBACK):
    try:
        ret = loc[parent][translation]
        #maybe this is futile, as the json file cannot be None?
        if ret is None:
            return fallback
        else:
            return ret
    except KeyError:
        return fallback

loc = loadTranslation()
