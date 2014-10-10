# -*- coding: UTF-8 -*-
import json


class Localizer():
    # Class for asking and reading which translation to use
    @staticmethod
    #def init():
    def getLocale(self):
        print("HEllo world")
        loc = json.loads(open("loc_fin.json").read())
        return loc
