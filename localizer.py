# -*- coding: UTF-8 -*-
import json


DEFAULT_FALLBACK = "Text missing"
DEFAULT_TRANSLATION = "loc_eng.json"


def loadTranslation(translation=DEFAULT_TRANSLATION):
    loc = json.loads(open(translation).read())
    return loc


def translate(parent, translation, fallback=DEFAULT_FALLBACK):
    try:
        ret = loc[parent][translation]
        #maybe this is futile, as the json file cannot be None?
        if ret is None:
            print("homohomo")
            return fallback
        else:
            return ret
    except KeyError:
        return fallback

loc = loadTranslation()
