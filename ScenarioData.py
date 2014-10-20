# -*- coding: UTF-8 -*-

import json
import View
import sys
import Object
from collections import OrderedDict
from os.path import dirname, abspath
import ModuleLocation
from client import Client
import shutil


class ScenarioData(object):

    def __init__(self, scenarioName):
        self.VERBOSE = True
        self.GAMEDATA_FOLDER = "gamedata"
        self.TEMPLATE_FOLDER = "%s/%s/%s/"\
            % (dirname(abspath(ModuleLocation.getLocation())),
                self.GAMEDATA_FOLDER, "template")

        self.texts = OrderedDict()
        self.roomList = []
        self.sequenceList = []
        self.customObjectList = []
        self.miscObjects = []
        self.startView = None
        self.endViewList = []
        self.menuList = []
        self.scenarioName = scenarioName

        self.dataDir = "%s/%s/%s/"\
            % (dirname(abspath(ModuleLocation.getLocation())),
                self.GAMEDATA_FOLDER, scenarioName)

    # Load and parse game data files
    def loadScenario(self):
        self.parseTexts()
        self.parseImages()
        #self.createInteractions()

    def parseTexts(self):
        try:
            with open(self.dataDir + "texts.json", encoding='utf-8') as f:
                self.texts = json.load(f)
                f.close()
        except FileNotFoundError:
            self.createFile("texts.json", self.dataDir)
            self.parseTexts()
            # This return statement is pointless here right now, but if
            # code is ever added below this except-clause, that code would
            # be executed twice if this wasn't here
            return

    def parseImages(self):
        try:
            with open(self.dataDir + "images.json", encoding='utf-8') as f:
                images = json.load(f)
                f.close()
        except FileNotFoundError:
            self.createFile("images.json", self.dataDir)
            # Once images.json is created, recursively call this function again
            self.parseImages()
            # Once the above function call is done, we must return so that
            # this function is not ran for the second time
            return

        try:
            with open(self.dataDir + "objects.json", encoding='utf-8') as f:
                objects = json.load(f)
                f.close()
        except FileNotFoundError:
            self.createFile("objects.json", self.dataDir)
            # Once the json is created, recursively call this function again
            self.parseImages()
            # Once the above function call is done, we must return so that
            # this function is not ran for the second time
            return

        # Parse objects from images.json and objects.json into categorized dict
        objectsByCat = OrderedDict()
        for child in images["children"]:
            layerObject = {}
            if ("object_name" in child["attrs"]):
                layerObject = objects[child["attrs"]["object_name"]]

            objectCategory = child["attrs"]["category"]
            objectId = child["attrs"]["id"]

            if not (objectCategory in objectsByCat):
                objectsByCat[objectCategory] = OrderedDict()

            # Leave misc objects as they are
            if (objectCategory == "misc"):
                self.miscObjects.append(child)
                continue

            layerChildren = None
            for layer in child:
                if (layer == "children"):
                    layerChildren = child[layer]
                elif (layer == "attrs"):
                    #layerAttrs = child[layer]
                    continue

            if not (layerChildren):
                continue

            # Go through the objects in the layer
            # And check for relation with objects.json objects
            createdObjects = OrderedDict()
            for item in layerChildren:
                itemId = item["attrs"]["id"]
                jsonImage = item["attrs"]

                # Get possible attributes from objects.json
                if ("object_name" in item["attrs"]):
                    itemId = item["attrs"]["object_name"]

                    try:
                        jsonObject = objects[itemId]
                    except KeyError:
                        print(
                            "Warning: Could not find object.json object for\
                            '%s' (object_name -> '%s')"
                            % (item["attrs"]["id"], itemId))

                elif (itemId in objects):
                    jsonObject = objects[itemId]

                elif not (itemId in objects):
                    jsonObject = {}

                # Create dict key for the item
                if not (itemId in createdObjects):
                    createdObjects[itemId] = {}

                createdObjects[itemId]["object"] = jsonObject
                createdObjects[itemId]["className"] = item["className"]

                if not ("image" in createdObjects[itemId]):
                    createdObjects[itemId]["image"] = []

                createdObjects[itemId]["image"].append(jsonImage)

            # Compose the final dict key and values
            objectsByCat[objectCategory][objectId] = {}
            objectsByCat[objectCategory][objectId]["image"] = createdObjects
            objectsByCat[objectCategory][objectId]["object"] = layerObject
            objectsByCat[objectCategory][objectId]["attrs"] = child["attrs"]
            objectsByCat[objectCategory][objectId]["className"] =\
                child["className"]

        #import pprint
        #pp = pprint.PrettyPrinter(indent=4)
        #pp.pprint(objectsByCat)

        # Create objects from the categorized dict
        for layer in objectsByCat:
            if (layer == "misc"):
                continue

            for child in objectsByCat[layer]:
                viewImages = objectsByCat[layer][child].pop("image")
                viewAttributes = objectsByCat[layer][child]

                if (layer == "room"):
                    self.addRoom(child, viewAttributes, viewImages)
                elif (layer == "sequence"):
                    self.addSequence(child, viewAttributes, viewImages)
                elif (layer == "start"):
                    self.addStart(viewAttributes, viewImages)
                elif (layer == "end"):
                    self.addEnd(child, viewAttributes, viewImages)
                elif (layer == "menu"):
                    self.addMenu(child, viewAttributes, viewImages)
                elif (layer == "custom"):
                    self.addCustomView(child, viewAttributes, viewImages)

        # Post-init sets triggers, outcomes etc.
        for obj in self.roomList + self.endViewList:
            obj.postInit(self.getGameObject)

        try:
            self.startView.postInit(self.getGameObject)
        except AttributeError as e:
            print("ScenarioData :: WARNING, startView is NoneType " +
                  "in parseImages")
            print("                " + str(e))

    # Creates necessary json files if they are not found
    # Basically just copies empty json files from the templates folder
    def createFile(self, filename, destination_folder):
        if self.VERBOSE:
            print("ScenarioData :: Creating " + filename + " from template.")
            #print("     " + self.TEMPLATE_FOLDER + filename)
            #print(" ->  " + destination_folder + filename)
        try:
            shutil.copy(self.TEMPLATE_FOLDER + filename,
                        destination_folder + filename)
        except FileNotFoundError as e:
            print("CRITICAL ERROR, Can't read gamedata/template folder")
            print(str(e))
            sys.exit(0)
        return

    # Save scenario to JSON files
    def saveScenario(self):
        if self.VERBOSE:
            print("ScenarioData :: saveScenario")
        #scenarioTexts = {}
        scenarioObjects = {}
        scenarioImages = []

        # Go through views
        for view in self.roomList + self.sequenceList + [self.startView] +\
                self.endViewList + self.menuList + self.customObjectList:
            viewChildren = []

            try:
                # Contents for objects.json from view
                if ("object_name" in view.attrs):
                    scenarioObjects[view.attrs["object_name"]] = view.object
            except AttributeError as e:
                print("ScenarioData :: " + str(e))

            try:
                # Go through objects inside views
                for viewChild in view.getChildren():
                    #childJSON = viewChild.objectAttributes
                    try:
                        # Go through images inside objects
                        for childImage in viewChild.images:
                            viewChildren.append(
                                self.__createLayerChildJSON__(
                                    childImage.imageAttributes,
                                    childImage.getClassname()))

                            # Contents for objects.json from image
                            if ("object_name" in childImage.imageAttributes):
                                scenarioObjects[
                                    childImage.imageAttributes["object_name"]]\
                                    = childImage.objectAttributes["object"]
                    except AttributeError as e:
                        print("ScenarioData :: " + str(e))

                    if (type(viewChild) == Object.JSONImage):
                        viewChildren.append(
                            self.__createLayerChildJSON__(
                                viewChild.imageAttributes,
                                viewChild.getClassname()
                                )
                            )
            except AttributeError as e:
                print("ScenarioData :: " + str(e))

            try:
                layerJSON = self.__createLayerJSON__(
                    view.attrs, viewChildren, view.classname)
                scenarioImages.append(layerJSON)
            except AttributeError as e:
                print("ScenarioData :: " + str(e))

        # Go through self.texts and add modified texts from objects
        objects = self.getAllObjects()[0]
        for obj in objects:
            for objectImage in obj.getImages():
                if (objectImage.id in self.texts):
                    self.texts[objectImage.id] = objectImage.texts

        # Miscellaneous objects
        for misc in self.miscObjects:
            scenarioImages.append(misc)

        # Bundle everything together
        scenarioAttrs = {"id": "Stage", "width": 981, "height": 643}
        scenarioChildren = self.__createLayerJSON__(
            scenarioAttrs, scenarioImages, "Stage")

        #These were unused
        textsJSON = json.dumps(
            self.texts, ensure_ascii=False, sort_keys=True, indent=4,
            separators=(',', ': '))
        imagesJSON = json.dumps(
            scenarioChildren, sort_keys=True, indent=4, separators=(',', ': '))
        objectsJSON = json.dumps(
            scenarioObjects, sort_keys=True, indent=4, separators=(',', ': '))

        #print(textsJSON)
        #print(imagesJSON)
        #print(objectsJSON)

        # Save into file
        f = open(self.dataDir + "texts.json", "w", encoding='utf-8')
        f.write(textsJSON)
        f.close()

        f = open(self.dataDir + "images.json", "w")
        f.write(imagesJSON)
        f.close()

        f = open(self.dataDir + "objects.json", "w")
        f.write(objectsJSON)
        f.close()

        # Upload the game to the server
        upload_folder = './' + self.GAMEDATA_FOLDER + '/' + self.scenarioName
        if self.VERBOSE:
            print("ScenarioData :: Uploading game files from " + upload_folder)
            print("                ( Client wants './gamedata/<game_name>' )")

        response = Client().upload_game_files(upload_folder)

        if response is None:
            print("ScenarioData :: Saving the game to the server failed.")
        elif response.status_code != 200:
            print("ScenarioData :: WARNING! Saving the game to " +
                  "the server failed! ("+response.status_code+")")
        elif self.VERBOSE:
            print("ScenarioData :: Save game successfull.")

    # Game object layers
    def __createLayerJSON__(self, attrs, children, className="Layer"):
        return {"attrs": attrs, "className": className, "children": children}

    # Single items for game layers
    def __createLayerChildJSON__(self, attrs, className="Image"):
        return {"attrs": attrs, "className": className}

    def getRoom(self, roomId):
        for room in self.roomList:
            if (room.id == roomId):
                return room

    def getRooms(self):
        return self.roomList

    def getRoomBackLoc(self, i):
        room = self.roomList[i]
        loc = self.dataDir + room.background.imageAttributes['src']
        return loc

    def getSequence(self, sequenceId):
        for sequence in self.sequenceList:
            if (sequence.id == sequenceId):
                return sequence

    def getObject(self, objectId):
        for room in self.roomList:
            for obj in room.objectList:
                if (obj.id == objectId):
                    return obj

    def getJSONObject(self, imageId):
        objects = self.getAllObjects()[0]
        for obj in objects:
            images = obj.getImages()
            for img in images:
                if (img.id == imageId):
                    return img

    def getCustomObject(self, objectId):
        for obj in self.customObjectList:
            if (obj.id == objectId):
                return obj

    # Get given types of objects found in rooms
    def getObjectsByType(self, objectTypes):
        retObjects = []
        if (type(objectTypes) != list or type(objectTypes) != tuple):
            objectTypes = (objectTypes)

        for room in self.roomList:
            roomObjects = {"room": room, "objects": []}
            for item in room.getItems():
                if (item.__class__.__name__.lower() in objectTypes):
                    roomObjects["objects"].append(item)
            if (len(roomObjects["objects"]) != 0):
                retObjects.append(roomObjects)
        return retObjects

    def getGeneralName(self, objectType):
        objectType = objectType.lower()
        if (objectType == "object"):
            return Object.Object.generalName
        elif (objectType == "item"):
            return Object.Item.generalName
        elif (objectType == "door"):
            return Object.Door.generalName
        elif (objectType == "container"):
            return Object.Container.generalName
        elif (objectType == "obstacle"):
            return Object.Obstacle.generalName

    # Get room, sequence or other object
    def getGameObject(self, objectType, objectId):
        objectType = objectType.lower()

        if (objectType == "room"):
            return self.getRoom(objectId)
        elif (objectType == "sequence"):
            return self.getSequence(objectId)
        elif (objectType == "object"):
            return self.getObject(objectId)
        elif (objectType == "menu"):
            return self.getMenu(objectId)
        elif (objectType == "custom"):
            return self.getCustomObject(objectId)

    # Get all right type of objects, amount of images and secrets,
    def getAllObjects(self):
        retObjects = []
        imgCount = 0
        secretCount = 0
        rightTypes = ["Object", "Item", "Container", "Door", "Obstacle"]

        for room in self.roomList:
            for obj in room.getItems():
                if (obj.__class__.__name__ in rightTypes and
                        obj.getClassname() != "Text"):

                        retObjects.append(obj)
                        imgCount += len(obj.getImages())
                        if (obj.getRepresentingImage()
                                .imageAttributes["category"] == "secret"):
                            secretCount += 1

        return [retObjects, imgCount, secretCount]

    def getMenu(self, menuId):
        for menu in self.menuList:
            if (menu.id == menuId):
                return menu

    def deleteObject(self, objectId):
        for obj in self.objectList:
            if obj.id == objectId:
                self.objectList.remove(obj)

        for room in self.roomList:
            roomObject = room.getObject(objectId)
            if (roomObject):
                room.deleteObject(objectId)

    def addEnd(self, endId, endAttributes, endImages):
        newView = View.End(self, endId, endAttributes, endImages)
        self.endViewList.append(newView)
        return newView

    def addStart(self, startAttributes, startImages):
        newView = View.Start(self, startAttributes, startImages)
        self.startView = newView
        return newView

    def addSequence(self, sequenceId, sequenceAttributes, sequenceImages):
        newView = View.Sequence(
            self, sequenceId, sequenceAttributes, sequenceImages)
        self.sequenceList.append(newView)
        return newView

    def addRoom(self, roomId, roomAttributes, roomImages):
        newView = View.Room(self, roomId, roomAttributes, roomImages)
        self.roomList.append(newView)
        return newView

    def addCustomView(self, viewId, viewAttributes, viewImages):
        newView = View.Custom(self, viewId, viewAttributes, viewImages)
        self.customObjectList.append(newView)
        return newView

    def addMenu(self, menuId, menuAttributes, menuImages):
        newView = View.Menu(self, menuId, menuAttributes, menuImages)
        self.menuList.append(newView)
        return newView

    def removeObject(self, gameObject):
        # Remove object text references in other objects
        # Objects include secrets
        if (gameObject.__class__.__name__ in ("Item", "Object")):
            for room in self.getObjectsByType(("item", "object")):
                for obj in room["objects"]:
                    #l = len(obj.texts)
                    obj.removeText(gameObject.id)

    # TODO: Remove menu, ends, starts, custom objects
    def removeView(self, viewObject):
        viewType = viewObject.__class__.__name__

        if (viewType == "Room"):
            # Remove text references
            self.roomList.remove(viewObject)

            for roomObject in viewObject.getItems():
                self.removeObject(roomObject)

        elif (viewType == "Sequence"):
            self.sequenceList.remove(viewObject)

if (__name__ == "__main__"):
    sc = ScenarioData()
    sc.loadScenario()
    sc.saveScenario()
