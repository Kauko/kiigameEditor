# -*- coding: UTF-8 -*-
import json
import Singleton


@Singleton
class Localizer():
    # Class for asking and reading which translation to use
    #def init():
    loc = ""
    DEFAULT_FALLBACK = "Text missing"

    @staticmethod
    def loadTranslation(self):
        self.loc = json.loads(open("loc_fin.json").read())

    def getLocale(self):
        return self.loc

    def translate(self, parent, translation, fallback=DEFAULT_FALLBACK):
        if self.loc == "":
            return fallback
        ret = self.loc[parent][translation]
        if ret is None:
            return fallback
        else:
            return ret
